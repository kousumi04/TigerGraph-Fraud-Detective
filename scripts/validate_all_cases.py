# scripts/validate_all_cases.py
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.app.models.schemas import BenchmarkCaseOutput

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def validate_benchmark_outputs():
    cases_dir = Path("cases")
    if not cases_dir.exists():
        logging.error("The cases/ directory does not exist.")
        return False

    case_files = list(cases_dir.glob("HHG-*.json"))
    expected_count = 20
    
    logging.info(f"Found {len(case_files)} JSON files in cases/.")
    
    if len(case_files) != expected_count:
        logging.warning(f"Benchmark requires exactly {expected_count} cases, but found {len(case_files)}.")

    passed = 0
    failed = 0

    for file_path in case_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 1. Pydantic Strict Schema Validation
            case_output = BenchmarkCaseOutput.model_validate(data)
            
            # 2. Logical Invariant Validation
            c = case_output.case
            if c.verdict == "fraud":
                assert len(c.affected_txn_ids) > 0, f"{file_path.name}: Fraud case must have affected_txn_ids."
                assert c.exposure_usd > 0, f"{file_path.name}: Fraud case must have exposure > 0."
                
            if c.verdict == "legitimate":
                assert len(c.affected_txn_ids) == 0, f"{file_path.name}: Legitimate case should not flag transactions."
                assert c.exposure_usd == 0, f"{file_path.name}: Legitimate case exposure must be 0."
                
            passed += 1
            
        except Exception as e:
            logging.error(f"Validation failed for {file_path.name}: {e}")
            failed += 1

    logging.info(f"Validation complete: {passed} passed, {failed} failed.")
    return failed == 0

if __name__ == "__main__":
    validate_benchmark_outputs()
