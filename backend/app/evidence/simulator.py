# backend/app/evidence/simulator.py
from typing import Dict, Any, Literal
from ..models.schemas import EvidenceRequest

class EvidenceSimulator:
    """
    Simulates customer or step-up authentication responses for the benchmark.
    """
    def __init__(self, mode: Literal["deterministic", "manual", "disabled"] = "deterministic"):
        self.mode = mode

    def simulate_request(self, request_type: str, step_count: int, context: Dict[str, Any]) -> tuple[EvidenceRequest, Dict[str, Any]]:
        """
        Generates a simulated response based on the current context probability.
        """
        assumed_status = "confirmed"
        
        if self.mode == "deterministic":
            # If the deterministic models already strongly suspect fraud, assume the customer denies it.
            prob = context.get("fraud_probability", 0.0)
            if prob > 0.6:
                assumed_status = "denied"
                
        elif self.mode == "disabled":
            assumed_status = "timeout"
            
        assumed_response = f"Simulated {request_type} result: {assumed_status}"
        
        request_record = EvidenceRequest(
            type=request_type if request_type in ["customer_validation", "step_up_auth", "analyst_info"] else "customer_validation",
            asked_after_step=step_count,
            assumed_response=assumed_response
        )
        
        response_data = {
            "status": assumed_status,
            "source": "simulated",
            "type": request_type
        }
        
        return request_record, response_data