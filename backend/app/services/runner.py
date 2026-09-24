# backend/app/services/runner.py
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any
from ..agent.workflow import build_investigation_graph
from ..validation.output_formatter import format_benchmark_output
from ..models.schemas import BenchmarkCaseOutput

logger = logging.getLogger(__name__)

# Resolve paths from this file so API/server launch directory cannot redirect
# case persistence away from the repository's cases/ directory.
graph = build_investigation_graph()
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CASES_DIR = PROJECT_ROOT / "cases"
CASES_DIR.mkdir(exist_ok=True)

async def run_investigation(case_id: str, trigger_data: Dict[str, Any]) -> BenchmarkCaseOutput:
    """Executes the full LangGraph investigation for a given case."""
    start_time = time.time()
    
    initial_state = {
        "case_id": case_id,
        "trigger": trigger_data,
        "tool_calls": 0,
        "tokens": 0,
        "errors": []
    }
    
    try:
        # Execute the state machine
        final_state = await graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Graph execution failed for {case_id}: {e}")
        # In a real scenario, we'd want a safe fallback state here
        raise

    latency = time.time() - start_time
    final_state["latency_s"] = latency
    
    # Format and validate strict schema
    output = format_benchmark_output(final_state)
    
    # Save the output to the cases/ directory as required by the benchmark
    output_path = CASES_DIR / f"{case_id}.json"
    temporary_path = output_path.with_suffix(".json.tmp")
    temporary_path.write_text(output.model_dump_json(indent=2), encoding="utf-8")
    temporary_path.replace(output_path)
        
    logger.info(f"Saved completed investigation to {output_path}")
    return output
