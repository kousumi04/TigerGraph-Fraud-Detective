# backend/app/policy/evaluator.py
from typing import List, Dict, Any
from .rules import (
    RuleR1, RuleR2, RuleR3, RuleR4, RuleR5,
    RuleR6, RuleR7, RuleR8, RuleR9, RuleR10,
    PolicyRule
)
from ..models.schemas import Action

class PolicyEngine:
    """
    Deterministic rule engine that prioritizes and evaluates
    compliance rules R1 through R10.
    """
    def __init__(self):
        self.rules: List[PolicyRule] = [
            RuleR10(),
            RuleR9(),
            RuleR7(),
            RuleR3(),
            RuleR2(),
            RuleR4(),
            RuleR6(),
            RuleR5(),
            RuleR8(),
            RuleR1()
        ]

    def evaluate_policy(self, context: Dict[str, Any]) -> List[Action]:
        triggered_actions: List[Action] = []
        applied_action_types = set()

        for rule in self.rules:
            action = rule.evaluate(context)
            if action and action.action not in applied_action_types:
                triggered_actions.append(action)
                applied_action_types.add(action.action)

        if not triggered_actions:
            triggered_actions.append(
                Action(
                    action="MONITOR_CARD",
                    route="auto",
                    reason="Default protective baseline active."
                )
            )

        return triggered_actions

    def validate_llm_actions(
        self,
        proposed_actions: List[str],
        context: Dict[str, Any]
    ) -> Tuple[bool, List[Action], str]:
        """
        Validates LLM-proposed actions against deterministic policy.
        Rejects proposals that violate hard compliance invariants.
        """
        policy_actions = self.evaluate_policy(context)
        valid_action_names = {a.action for a in policy_actions}
        
        # Check if proposed actions conflict with mandatory actions (e.g. mandatory SAR)
        must_file_sar = any(a.action == "FILE_REPORT" for a in policy_actions)
        llm_filed_sar = "FILE_REPORT" in proposed_actions

        if must_file_sar and not llm_filed_sar:
            return False, policy_actions, "Violation: R7 requires FILE_REPORT, but LLM omitted it."

        return True, policy_actions, "LLM recommendation adheres to policy constraints."