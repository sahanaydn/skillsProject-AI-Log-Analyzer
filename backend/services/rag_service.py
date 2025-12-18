from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
import re
import numpy as np
import faiss
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
    day = dt.strftime("%d").lstrip("0")
    year = dt.strftime("%Y")
    variants.add(f"{month} {day}")
    variants.add(f"{day} {month}")
    variants.add(f"{month} {day}, {year}")
    variants.add(f"{month} {day} {year}")


def _generate_query_variants(query: str) -> List[str]:
    base = query.lower().strip()
    variants = {base}

    def remove_ordinals(text: str) -> str:
        return re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", text)

    variants.add(remove_ordinals(base))
    variants.add(base.replace(",", ""))
    variants.add(remove_ordinals(base.replace(",", "")))

    month_pattern = re.compile(
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:,\s*(\d{4}))?"
    )
    for match in month_pattern.finditer(base):
        month = match.group(1)
        day = match.group(2)
        year = match.group(3) or datetime.now().strftime("%Y")
        variants.add(f"{month} {day}")
        variants.add(f"{day} {month}")
        variants.add(f"{month} {day}, {year}")

    if latest_log_timestamp:
        relative_patterns = [
            (re.compile(r"(last|past)\s+24\s+hours"), timedelta(hours=24)),
            (re.compile(r"(last|past)\s+day"), timedelta(days=1)),
        ]
        for pattern, delta in relative_patterns:
            if pattern.search(base):
                _add_date_variants_for_datetime(latest_log_timestamp, variants)
                _add_date_variants_for_datetime(latest_log_timestamp - delta, variants)

    return [variant for variant in variants if variant]


def _keyword_chunk_search(query: str, limit: int = 3) -> List[str]:
    variants = _generate_query_variants(query)
    if not variants:
        return []

    matches = []
    for chunk in log_chunks_storage:
        lowered = chunk.lower()
        if any(variant in lowered for variant in variants):
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
