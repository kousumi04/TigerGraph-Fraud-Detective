# backend/app/fraud/scoring.py
from typing import Dict, Any, Tuple, List

class FraudScorer:
    """
    Deterministic fraud scoring model producing transparent,
    auditable score contributions.
    """
    WEIGHTS = {
        "card_testing": 0.35,
        "card_not_present": 0.20,
        "new_device": 0.15,
        "out_of_region": 0.15,
        "account_takeover": 0.40,
        "shared_fraud_device": 0.30,
        "shared_fraud_region": 0.10,
        "connected_card_anomaly": 0.25,
        "customer_denial": 0.50,
        "customer_confirmation": -0.60
    }

    @classmethod
    def calculate_probability(
        cls,
        detector_results: Dict[str, bool],
        graph_signals: Dict[str, Any],
        simulation_signal: Dict[str, Any] = None
    ) -> Tuple[float, List[Dict[str, Any]]]:
        base_probability = 0.05
        contributions: List[Dict[str, Any]] = [
            {"signal": "baseline_prior", "contribution": base_probability}
        ]
        
        score = base_probability

        # Pattern contributions
        for pattern_name, matched in detector_results.items():
            if matched and pattern_name in cls.WEIGHTS:
                weight = cls.WEIGHTS[pattern_name]
                score += weight
                contributions.append({"signal": pattern_name, "contribution": weight})

        # Graph signals
        if graph_signals.get("shares_device_with_fraud", False):
            w = cls.WEIGHTS["shared_fraud_device"]
            score += w
            contributions.append({"signal": "shares_fraud_device", "contribution": w})

        if graph_signals.get("connected_fraud_cards_count", 0) > 0:
            w = cls.WEIGHTS["connected_card_anomaly"]
            score += w
            contributions.append({"signal": "connected_cards_flagged", "contribution": w})

        # The bank score is an alert prior, never a verdict. Keep its impact
        # deliberately small so structural evidence and customer evidence win.
        risk_score = graph_signals.get("risk_score")
        if risk_score is not None:
            risk_adjustment = (float(risk_score) - 0.5) * 0.20
            score += risk_adjustment
            contributions.append({"signal": "risk_score_prior", "contribution": round(risk_adjustment, 4)})

        # Simulated customer response signals
        if simulation_signal:
            status = simulation_signal.get("status")
            if status == "denied":
                w = cls.WEIGHTS["customer_denial"]
                score += w
                contributions.append({"signal": "customer_denial", "contribution": w})
            elif status == "confirmed":
                w = cls.WEIGHTS["customer_confirmation"]
                score += w
                contributions.append({"signal": "customer_confirmation", "contribution": w})

        # Bounded probability in [0.0, 1.0]
        final_probability = max(0.0, min(1.0, score))
        return round(final_probability, 4), contributions
