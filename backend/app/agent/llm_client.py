# backend/app/agent/llm_client.py
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from langchain_openai import ChatOpenAI
from httpx import HTTPStatusError
from ..config import settings
from ..models.schemas import LLMInvestigationAssessment

logger = logging.getLogger(__name__)

def get_llm_client() -> ChatOpenAI:
    """Configures the LLM client based on the chosen free provider."""
    base_urls = {
        "openrouter": "https://openrouter.ai/api/v1",
        "cerebras": "https://api.cerebras.ai/v1",
        "huggingface": "https://api-inference.huggingface.co/v1",
        "groq": "https://api.groq.com/openai/v1"  # Added Groq endpoint
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
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(HTTPStatusError),
    before_sleep=lambda retry_state: logger.warning(f"Rate limited. Retrying LLM call... Attempt {retry_state.attempt_number}")
)
def assess_evidence_with_llm(evidence_packet_str: str) -> LLMInvestigationAssessment:
    """
    Forces the LLM to synthesize the evidence packet into a structured assessment.
    """
    llm = get_llm_client()
    structured_llm = llm.with_structured_output(LLMInvestigationAssessment)
    
    prompt = f"""
    You are a Senior Fraud Investigator. Analyze the following evidence packet.
    Determine the fraud probability, identify any patterns, and state if critical information is missing.
    Do NOT invent evidence. Base your reasoning strictly on the provided packet.
    
    {evidence_packet_str}
    """
    
    response = structured_llm.invoke(prompt)
    return response