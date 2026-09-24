# backend/app/api/endpoints.py
from fastapi import APIRouter, HTTPException, Path as APIPath
from pydantic import BaseModel
from typing import List
from ..services.runner import run_investigation
from ..models.schemas import BenchmarkCaseOutput
import os
import json
from pathlib import Path

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CASES_DIR = PROJECT_ROOT / "cases"

class TriggerPayload(BaseModel):
    transaction_id: str
    risk_score: float

@router.get("/health")
def health_check():
    return {"status": "operational"}

@router.get("/system/status")
def system_status():
    return {
        "mcp_connected": True,
        "llm_provider_active": True,
        "vector_store_loaded": True
    }

@router.get("/cases", response_model=List[str])
def list_completed_cases():
    """Returns a list of completed benchmark case IDs."""
    if not CASES_DIR.exists():
        return []
    return [f.stem for f in CASES_DIR.glob("*.json")]

@router.get("/cases/{case_id}", response_model=BenchmarkCaseOutput)
def get_case(case_id: str = APIPath(..., description="The case ID (e.g., HHG-001)")):
    """Retrieves a completed case JSON from disk."""
    case_path = CASES_DIR / f"{case_id}.json"
    if not case_path.exists():
        raise HTTPException(status_code=404, detail="Case not found")
    
    with open(case_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return BenchmarkCaseOutput(**data)

@router.post("/cases/{case_id}/investigate", response_model=BenchmarkCaseOutput)
async def investigate_case(payload: TriggerPayload, case_id: str = APIPath(...)):
    """Triggers the LangGraph agent to investigate a new transaction."""
    try:
        result = await run_investigation(case_id, payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Investigation failed: {str(e)}")
