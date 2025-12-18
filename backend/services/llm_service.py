import os
import json
from typing import List, Dict, Any
import google.generativeai as genai

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("--- DEBUG: GOOGLE_API_KEY environment variable not found. ---")
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    
    print(f"--- DEBUG: Loaded API Key starts with '{api_key[:5]}' and ends with '{api_key[-4:]}' ---")

    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"Error during API configuration: {e}")

async def _call_gemini(prompt: str, is_json: bool = True) -> Dict | str:
    model = genai.GenerativeModel('gemini-2.5-flash')
    try:
        response = await model.generate_content_async(prompt)
        text_response = response.text
        
        if is_json:
            json_str = text_response.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(json_str)
        return text_response
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise ConnectionError(f"Failed to get a valid response from the AI model: {e}")

async def get_summary_report(log_data: List[str]) -> Dict[str, Any]:
    log_sample = "\n".join(log_data[:300])

    prompt = f"""
**INSTRUCTION:**
You are a senior DevOps engineer. Analyze the following sample of a log file and generate a summary report in JSON format.
The report must include two keys:
1. `top_incidents`: A list of the 3-5 most critical or frequent issues found in the logs. Each item in the list should be a JSON object with keys `title`, `timestamp`, and `severity`.
2. `recommended_actions`: A list of 3-5 concrete, actionable steps to address the identified issues. Each item should be a string.

**LOG FILE SAMPLE:**
---
{log_sample}
---

**OUTPUT FORMAT (JSON only):**
{{
  "top_incidents": [
    {{"title": "Example: Database connection timeout", "timestamp": "YYYY-MM-DD HH:MM:SS", "severity": "ERROR"}}
  ],
  "recommended_actions": [
    "Example: Increase the database connection pool size."
  ]
}}
"""
    return await _call_gemini(prompt)

async def get_chat_response(query: str, relevant_chunks: List[str], global_stats: Dict[str, Any]) -> Dict[str, Any]:
    context_str = "\n---\n".join(relevant_chunks)

    prompt = f"""**FILE SUMMARY CONTEXT:**
- Total Lines: {global_stats.get('total_lines', 'N/A')}
- Total Errors: {global_stats.get('total_errors', 'N/A')}
- Total Warnings: {global_stats.get('total_warnings', 'N/A')}

**DETAILED LOG SNIPPETS (Context for the query):**
---
{context_str}
---

**INSTRUCTION:**
You are a helpful AI assistant for analyzing logs. Based on the file summary and the detailed log snippets, answer the user's query.
Your response MUST be in JSON format with the following keys:
1. `answer`: A clear, direct answer to the user's query. If you cannot answer from the context, state that clearly.
2. `suggested_followup`: A list of 2-3 relevant follow-up questions the user might want to ask. If there are no good suggestions, return an empty list.
Your answer should be based *only* on the provided context.

**User Query:** {query}

**OUTPUT FORMAT (JSON only):**
{{
  "answer": "Your direct answer here.",
  "suggested_followup": ["A follow-up question?", "Another one?"]
}}
"""
    response_json = await _call_gemini(prompt)
    
    response_json['relevant_logs'] = relevant_chunks
    
    return response_json
