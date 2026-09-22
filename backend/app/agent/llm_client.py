# backend/app/agent/llm_client.py
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from langchain_openai import ChatOpenAI
from httpx import HTTPStatusError
from ..config import settings
from ..models.schemas import LLMInvestigationAssessment

logger = logging.getLogger(__name__)

def get_llm_client() -> ChatOpenAI:
    base_urls = {
        "openrouter": "https://openrouter.ai/api/v1",
        "cerebras": "https://api.cerebras.ai/v1",
        "huggingface": "https://api-inference.huggingface.co/v1",
        "groq": "https://api.groq.com/openai/v1"
    }
    base_url = base_urls.get(settings.llm_provider, base_urls["openrouter"])
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=base_url,
        temperature=0.1,
        max_retries=0
    )

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=6),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(HTTPStatusError),
    before_sleep=lambda retry_state: logger.warning(f"Rate limited. Retrying LLM call... Attempt {retry_state.attempt_number}")
)
def assess_evidence_with_llm(evidence_packet_str: str) -> tuple[LLMInvestigationAssessment, int]:
    llm = get_llm_client()
    structured_llm = llm.with_structured_output(LLMInvestigationAssessment, include_raw=True)
    
    prompt = f"""
    You are a Senior Fraud Investigator. Analyze the following evidence packet.
    Determine the fraud probability (0.0 to 1.0), identify patterns (e.g. card_testing, card_not_present, card_not_present_new_device, out_of_region_use, account_takeover, undocumented, or none), and state if critical information is missing.
    Do NOT invent evidence. Base your reasoning strictly on the provided packet.
    
    {evidence_packet_str}
    """
    
    response = structured_llm.invoke(prompt)
    raw_msg = response.get("raw")
    token_usage = 0
    if raw_msg and hasattr(raw_msg, "response_metadata"):
        usage = raw_msg.response_metadata.get("token_usage", {})
        token_usage = usage.get("total_tokens", 0)
    
    return response["parsed"], token_usage