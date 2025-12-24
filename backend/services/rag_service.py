from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
import re
import numpy as np
import faiss
from dateutil import parser as dateutil_parser
from sentence_transformers import SentenceTransformer

faiss_index: faiss.Index | None = None
log_chunks_storage: List[str] = []
global_log_stats: Dict[str, Any] = {}
latest_log_timestamp: datetime | None = None
_TIMESTAMP_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})")

print("Loading sentence transformer model...")
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

def _create_faiss_index(dimension: int) -> faiss.Index:
    return faiss.IndexFlatL2(dimension)

def _choose_bucket_size(span: timedelta) -> int:
    if span <= timedelta(hours=2):
        return 1
    if span <= timedelta(hours=24):
        return 5
    if span <= timedelta(days=7):
        return 60
    if span <= timedelta(days=14):
        return 180
    return 720


def _floor_timestamp(dt: datetime, bucket_minutes: int) -> datetime:
    bucket_seconds = bucket_minutes * 60
    floored_seconds = int(dt.timestamp() // bucket_seconds * bucket_seconds)
    return datetime.fromtimestamp(floored_seconds)


def _extract_timestamp(line: str) -> datetime | None:
    match = _TIMESTAMP_PATTERN.match(line)
    if not match:
        return None
    try:
        return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _augment_line_with_human_date(line: str) -> str:
    timestamp = _extract_timestamp(line)
    if not timestamp:
        return line

    human_text = timestamp.strftime("%B %d, %Y %H:%M:%S")
    return f"{line} | DateText: {human_text}"


def _parse_log_stats(log_lines: List[str]) -> Dict[str, Any]:
    stats = {
        "counts": defaultdict(int),
        "time_series": defaultdict(lambda: defaultdict(int)),
        "error_types": defaultdict(int)
    }
    error_keywords = {
        "Timeout": r"connection timed out",
        "Auth Fail": r"authentication failed|invalid credentials",
        "DB Error": r"failed to connect to database|database connection",
        "Null Pointer": r"nullpointerexception",
        "Payment Failed": r"payment failed"
    }

    parsed_events = []

    for line in log_lines:
        try:
            timestamp = _extract_timestamp(line)
            lower_line = line.lower()

            if 'error' in lower_line:
                stats["counts"]["ERROR"] += 1
                if timestamp:
                    parsed_events.append((timestamp, "errors"))
                else:
                    stats["time_series"]["unknown"]["errors"] += 1
                found_category = False
                for category, pattern in error_keywords.items():
                    if re.search(pattern, lower_line):
                        stats["error_types"][category] += 1
                        found_category = True
                        break
                if not found_category:
                    stats["error_types"]["Generic Error"] += 1
            elif 'warning' in lower_line:
                stats["counts"]["WARNING"] += 1
                if timestamp:
                    parsed_events.append((timestamp, "warnings"))
                else:
                    stats["time_series"]["unknown"]["warnings"] += 1
            else:
                stats["counts"]["INFO"] += 1
        except Exception:
            continue

    if parsed_events:
        timestamps = [event[0] for event in parsed_events]
        span = max(timestamps) - min(timestamps) if len(timestamps) > 1 else timedelta()
        bucket_size = _choose_bucket_size(span)
        for ts, key in parsed_events:
            bucket_time = _floor_timestamp(ts, bucket_size)
            if bucket_size >= 1440:
                time_key = bucket_time.strftime("%Y-%m-%d")
            elif bucket_size >= 60:
                time_key = bucket_time.strftime("%Y-%m-%d %H:%M")
            else:
                time_key = bucket_time.strftime("%Y-%m-%d %H:%M")
            stats["time_series"][time_key][key] += 1

    sorted_time_series = sorted(stats["time_series"].items())
    return {
        "counts": dict(stats["counts"]),
        "time_series": [{"time": time, "errors": data.get("errors", 0), "warnings": data.get("warnings", 0)} for time, data in sorted_time_series],
        "error_types": [{"name": name, "count": count} for name, count in stats["error_types"].items()]
    }

def process_log_file(log_data: List[str]) -> Dict[str, Any]:
    global faiss_index, log_chunks_storage, global_log_stats

    chunk_size = 5
    overlap = 2
    step = chunk_size - overlap
    timestamps: List[datetime] = []
    augmented_lines = []
    for line in log_data:
        ts = _extract_timestamp(line)
        if ts:
            timestamps.append(ts)
        augmented_lines.append(_augment_line_with_human_date(line))

    chunks = [
        "\n".join(augmented_lines[i:i + chunk_size])
        for i in range(0, len(augmented_lines), step)
    ]
    log_chunks_storage = chunks

    embeddings = sentence_model.encode(chunks, convert_to_tensor=False)
    dimension = embeddings.shape[1]

    index = _create_faiss_index(dimension)
    index.add(np.array(embeddings, dtype=np.float32))
    faiss_index = index

    total_lines = len(log_data)
    parsed_stats = _parse_log_stats(log_data)
    
    stats_summary = {
        "total_lines": total_lines,
        "total_errors": parsed_stats["counts"].get("ERROR", 0),
        "total_warnings": parsed_stats["counts"].get("WARNING", 0),
    }
    global latest_log_timestamp
    if timestamps:
        latest_log_timestamp = max(timestamps)
        stats_summary["latest_timestamp"] = latest_log_timestamp.isoformat()
        stats_summary["earliest_timestamp"] = min(timestamps).isoformat()
    else:
        latest_log_timestamp = None

    global_log_stats = stats_summary

    return {
        "message": "Log file analyzed successfully.",
        "total_lines": total_lines,
        "total_chunks": len(chunks),
        "log_stats": parsed_stats,
    }


def _add_date_variants_for_datetime(dt: datetime, variants: set[str]) -> None:
    month = dt.strftime("%B").lower()
    year = dt.strftime("%Y")
    
    # Generate variants for both padded ('08') and non-padded ('8') days
    day_padded = dt.strftime("%d")
    day_unpadded = day_padded.lstrip("0")
    
    # Use a set to avoid duplicates if day is two digits (e.g., '13' and lstrip('0') is still '13')
    days_to_try = {day_padded, day_unpadded}

    for day in days_to_try:
        if not day: continue # handles case where day is '00' or similar, lstrip makes it empty
        variants.add(f"{month} {day}")
        variants.add(f"{day} {month}")
        variants.add(f"{month} {day}, {year}")
        variants.add(f"{month} {day} {year}")


def _generate_query_variants(query: str) -> List[str]:
    base_query = query.lower().strip()
    variants = {base_query}

    def remove_ordinals(text: str) -> str:
        return re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", text)

    cleaned_query = remove_ordinals(base_query)
    cleaned_query = cleaned_query.replace(",", "")
    variants.add(cleaned_query)

    try:
        month_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
        match = re.search(month_pattern, cleaned_query, re.IGNORECASE)

        if match:
            start_pos = max(0, match.start() - 15)
            end_pos = min(len(cleaned_query), match.end() + 15)
            substring_to_parse = cleaned_query[start_pos:end_pos]
            parsed_date = dateutil_parser.parse(substring_to_parse, fuzzy=True)
        else:
            parsed_date = dateutil_parser.parse(cleaned_query, fuzzy=True)

        _add_date_variants_for_datetime(parsed_date, variants)
    except (ValueError, TypeError):
        pass

    if latest_log_timestamp:
        relative_patterns = [
            (re.compile(r"(last|past)\s+24\s+hours"), timedelta(hours=24)),
            (re.compile(r"(last|past)\s+day"), timedelta(days=1)),
        ]
        for pattern, delta in relative_patterns:
            if pattern.search(base_query):
                _add_date_variants_for_datetime(latest_log_timestamp, variants)
                _add_date_variants_for_datetime(latest_log_timestamp - delta, variants)
    
    return [variant for variant in variants if variant]


def _keyword_chunk_search(query: str, limit: int = 3) -> List[str]:
    # Get all variants, including date and original query text
    all_variants = _generate_query_variants(query)

    # Isolate content keywords from the original query to make the search more specific
    query_words = set(query.lower().split())
    date_related_words = {
        "january", "february", "march", "april", "may", "june", "july",
        "august", "september", "october", "november", "december",
        "last", "past", "hours", "day"
    }
    # Add common ordinals and numbers
    date_related_words.update(str(d) for d in range(1, 32))
    date_related_words.update(f"{d}{s}" for d in range(1, 32) for s in ["st", "nd", "rd", "th"])

    stopwords = {"what", "is", "teh", "the", "on", "in", "from", "observed", "most", "common", "a", "were", "of", "find", "all"}

    # Identify content keywords by removing stopwords and date-related words
    content_keywords = query_words - stopwords - date_related_words

    matches = []
    for chunk in log_chunks_storage:
        lowered_chunk = chunk.lower()

        # The chunk must contain a match for one of the generated date variants
        has_date_match = any(variant in lowered_chunk for variant in all_variants)
        if not has_date_match:
            continue

        # Additionally, the chunk must contain ALL of the identified content keywords.
        if not content_keywords or all(keyword in lowered_chunk for keyword in content_keywords):
            matches.append(chunk)

        if len(matches) >= limit:
            break
    
    return matches


def search_relevant_chunks(query: str) -> List[str]:
    if not faiss_index:
        return []

    keyword_matches = _keyword_chunk_search(query)
    if keyword_matches:
        return keyword_matches

    query_embedding = sentence_model.encode([query], convert_to_tensor=False)
    k = 3
    distances, indices = faiss_index.search(np.array(query_embedding, dtype=np.float32), k)
    
    if not indices.size:
        return []
        
    relevant_chunks = [log_chunks_storage[i] for i in indices[0]]
    return relevant_chunks

def get_global_stats() -> Dict[str, Any]:
    return global_log_stats

def is_ready() -> bool:
    return faiss_index is not None
