# backend/app/policy/approval_routes.py
from enum import Enum

class ApprovalRoute(str, Enum):
    AUTO = "auto"
    L1 = "L1"
    L2 = "L2"