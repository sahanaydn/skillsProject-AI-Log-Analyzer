from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

from services import rag_service, llm_service

class QueryRequest(BaseModel):
    query: str

app = FastAPI(title="AI Log Analyzer API [Hackathon Edition]")

raw_log_data_storage: List[str] = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "AI Log Analyzer API is running."}

@app.post("/upload")
async def upload_log_file(file: UploadFile = File(...)):
    global raw_log_data_storage
    try:
        contents = await file.read()
        log_data = contents.decode('utf-8').splitlines()
        
        if not log_data:
            raise HTTPException(status_code=400, detail="Log file is empty.")

        raw_log_data_storage = log_data

        analysis_result = rag_service.process_log_file(log_data)
        
        log_stats = analysis_result.get('log_stats', {})
        
        return {
            "message": analysis_result.get("message"),
            "total_lines": analysis_result.get("total_lines"),
            "severity_breakdown": log_stats.get('counts', {}),
            "time_series": log_stats.get('time_series', []),
            "error_types": log_stats.get('error_types', [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during upload: {str(e)}")

@app.get("/summary")
async def get_log_summary():
    if not rag_service.is_ready() or not raw_log_data_storage:
        raise HTTPException(status_code=400, detail="No log file has been analyzed yet. Please call /upload first.")
    
    try:
        summary_report = await llm_service.get_summary_report(raw_log_data_storage)
        return summary_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@app.post("/query")
async def query_logs(request: QueryRequest):
    if not rag_service.is_ready():
        raise HTTPException(status_code=400, detail="No log file has been analyzed yet. Please call /upload first.")

    try:
        relevant_chunks = rag_service.search_relevant_chunks(request.query)
        
        global_stats = rag_service.get_global_stats()
        
        response = await llm_service.get_chat_response(request.query, relevant_chunks, global_stats)
        
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during chat: {str(e)}")
