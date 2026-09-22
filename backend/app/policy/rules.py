# backend/app/policy/rules.py
from typing import List, Dict, Any, Optional
from .action_catalog import FraudAction
from .approval_routes import ApprovalRoute
from ..models.schemas import Action

class PolicyRule:
    def __init__(self, rule_id: str, description: str):
        self.rule_id = rule_id
        self.description = description

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        raise NotImplementedError

class RuleR1(PolicyRule):
    """R1: Low risk confirmed (< 0.15) with no structural anomalies -> Auto Allow & Close."""
    def __init__(self):
        super().__init__("R1", "Low risk confirmed without structural anomalies")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("fraud_probability", 1.0) <= 0.15 and not context.get("anomalies_present", False):
            return Action(
                action=FraudAction.CLOSE_NO_FRAUD.value,
                route=ApprovalRoute.AUTO.value,
                reason="R1: Low risk score with negative anomaly indicators verified."
            )
        return None

class RuleR2(PolicyRule):
    """R2: Confirmed Card Testing pattern -> Decline Transaction & Block Card."""
    def __init__(self):
        super().__init__("R2", "Card testing velocity detected")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("pattern") == "card_testing":
            return Action(
                action=FraudAction.BLOCK_CARD.value,
                route=ApprovalRoute.AUTO.value,
                reason="R2: Velocity micro-authorizations matched card testing profile."
            )
        return None

class RuleR3(PolicyRule):
    """R3: Account Takeover indicators -> Block All Associated Cards & Escalate L2."""
    def __init__(self):
        super().__init__("R3", "Account Takeover critical signals")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("pattern") == "account_takeover":
            return Action(
                action=FraudAction.BLOCK_ALL_CARDS.value,
                route=ApprovalRoute.L2.value,
                reason="R3: Multi-attribute ATO signal verified across device and credentials."
            )
        return None

class RuleR4(PolicyRule):
    """R4: New device CNP with moderate probability -> Require Step-Up Auth."""
    def __init__(self):
        super().__init__("R4", "Unrecognized device CNP authentication challenge")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("pattern") == "card_not_present_new_device" and 0.35 <= context.get("fraud_probability", 0.0) < 0.85:
            return Action(
                action=FraudAction.STEP_UP_AUTH.value,
                route=ApprovalRoute.AUTO.value,
                reason="R4: Moderate probability on unrecognized device footprint."
            )
        return None

class RuleR5(PolicyRule):
    """R5: Out of region activity without travel flag -> Monitor Card and Warn Customer."""
    def __init__(self):
        super().__init__("R5", "Geographic deviation from primary card footprint")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("pattern") == "out_of_region_use":
            return Action(
                action=FraudAction.WARN_CUSTOMER.value,
                route=ApprovalRoute.AUTO.value,
                reason="R5: Deviation from registered regional transaction baseline."
            )
        return None

class RuleR6(PolicyRule):
    """R6: Graph syndication: Multiple cards sharing tainted devices -> Monitor Connected Cards."""
    def __init__(self):
        super().__init__("R6", "Multi-card device network clustering")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if len(context.get("connected_card_ids", [])) > 1:
            return Action(
                action=FraudAction.MONITOR_CONNECTED_CARDS.value,
                route=ApprovalRoute.L1.value,
                reason="R6: Shared hardware topology detected across distinct card identifiers."
            )
        return None

class RuleR7(PolicyRule):
    """R7: Exposure USD >= $5,000 or high fraud certainty -> Mandatory Regulatory Filing (SAR)."""
    def __init__(self):
        super().__init__("R7", "High exposure threshold or high-certainty fraud filing requirement")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        exposure = float(context.get("exposure_usd", 0.0))
        prob = float(context.get("fraud_probability", 0.0))
        if exposure >= 5000.0 or prob >= 0.85:
            return Action(
                action=FraudAction.FILE_REPORT.value,
                route=ApprovalRoute.L2.value,
                reason=f"R7: Regulatory filing triggered (Exposure: ${exposure:.2f}, Probability: {prob:.2f})."
            )
        return None

class RuleR8(PolicyRule):
    """R8: Undocumented coordinated pattern -> Create Case & Escalate to L1."""
    def __init__(self):
        super().__init__("R8", "Undocumented multi-hop coordination")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("pattern") == "undocumented":
            return Action(
                action=FraudAction.ESCALATE_TO_ANALYST.value,
                route=ApprovalRoute.L1.value,
                reason="R8: Novel topological pattern requires human analyst review."
            )
        return None

class RuleR9(PolicyRule):
    """R9: Customer verification denial received -> Immediately Block All Cards and Escalate."""
    def __init__(self):
        super().__init__("R9", "Explicit customer denial of transaction")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("customer_response") == "denied":
            return Action(
                action=FraudAction.BLOCK_ALL_CARDS.value,
                route=ApprovalRoute.L1.value,
                reason="R9: Customer confirmed transaction was unauthorized."
            )
        return None

class RuleR10(PolicyRule):
    """R10: Customer confirms valid transaction -> Clear Flag and Close."""
    def __init__(self):
        super().__init__("R10", "Explicit customer authentication confirmed")

    def evaluate(self, context: Dict[str, Any]) -> Optional[Action]:
        if context.get("customer_response") == "confirmed":
            return Action(
                action=FraudAction.ALLOW_TRANSACTION.value,
                route=ApprovalRoute.AUTO.value,
                reason="R10: Transaction validity confirmed by legitimate cardholder."
            )
        return None