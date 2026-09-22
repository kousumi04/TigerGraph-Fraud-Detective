# backend/app/fraud/undocumented.py
from typing import Dict, Any, Tuple

def detect_undocumented_pattern(
    pattern_matches: Dict[str, bool],
    risk_score: float,
    graph_connections_count: int
) -> Tuple[bool, str]:
    """
    Flags coordinated or repeated abuse that does not conform to the 5 standard patterns.
    """
    has_known_pattern = any(pattern_matches.values())
    
    # If no standard pattern matched, but graph connections or trigger risk are critically high
    if not has_known_pattern and (risk_score >= 0.75 or graph_connections_count >= 5):
        desc = (
            f"Anomalous transaction cluster with risk score {risk_score:.2f} "
            f"and {graph_connections_count} cross-entity graph linkages exhibiting non-standard behavior."
        )
        return True, desc

    return False, ""