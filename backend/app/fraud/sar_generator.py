# backend/app/fraud/sar_generator.py
import logging
from typing import Dict, Any, List
from ..agent.llm_client import get_llm_client
from ..models.schemas import SAR
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class SARDraft(BaseModel):
    narrative: str = Field(..., description="6 to 12 sentences covering WHO, WHAT, WHEN, WHERE, HOW, and WHY SUSPICIOUS.")
    subjects: List[str] = Field(..., description="List of entity IDs involved.")

def generate_sar(state: Dict[str, Any]) -> SAR:
    """
    Drafts a Suspicious Activity Report if the policy requires it.
    Strictly bounds the LLM to the provided evidence packet.
    """
    if not state.get("sar_required", False):
        return SAR(file=False)

    try:
        llm = get_llm_client()
        structured_llm = llm.with_structured_output(SARDraft)
        
        packet = state.get("evidence_packet", {})
        exposure = sum(t.get("amount", 0.0) for t in state.get("transaction_evidence", []))
        dates = [t.get("ts") for t in state.get("transaction_evidence", []) if "ts" in t]
        
        prompt = f"""
        Generate a Suspicious Activity Report (SAR) narrative based strictly on this evidence:
        {packet}
        
        Requirements:
        - Exactly 6 to 12 sentences.
        - Must include WHO, WHAT, WHEN, WHERE, HOW, and WHY SUSPICIOUS.
        - Do not invent names, amounts, or dates. Use only the provided IDs and values.
        """
        
        draft = structured_llm.invoke(prompt)
        
        return SAR(
            file=True,
            reason="Policy threshold triggered mandatory SAR filing.",
            narrative=draft.narrative,
            subjects=draft.subjects,
            total_amount_usd=exposure,
            activity_dates=[str(d) for d in dates if d]
        )
    except Exception as e:
        logger.error(f"SAR Generation failed: {e}")
        # Fallback deterministic SAR to guarantee schema compliance
        return SAR(
            file=True,
            reason="Automated fallback due to generation error.",
            narrative=f"Suspicious activity detected on case {state.get('case_id')}. Automated pattern match identified. Further investigation required.",
            subjects=[state.get("case_id", "Unknown")],
            total_amount_usd=0.0,
            activity_dates=[]
        )