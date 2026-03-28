import random
import time

# Confidence routing thresholds
AUTO_APPROVE_THRESHOLD = 92
MANUAL_REVIEW_THRESHOLD = 75


def verify_kyc(retry: bool = False, aadhaar_suffix: str = "") -> dict:
    """
    Simulates KYC with realistic confidence distribution.
    - First attempt: 70% chance high confidence, 20% medium, 10% fail
    - Retry: always high confidence
    Confidence routing:
      >= 92  → auto approve
      75-91  → proceed with flag
      < 75   → escalate immediately
    """
    if retry:
        confidence = random.randint(92, 99)
    else:
        roll = random.random()
        if roll < 0.70:
            confidence = random.randint(88, 99)   # high
        elif roll < 0.90:
            confidence = random.randint(75, 87)   # medium
        else:
            confidence = random.randint(40, 74)   # fail

    kyc_verified = confidence >= MANUAL_REVIEW_THRESHOLD

    if confidence >= AUTO_APPROVE_THRESHOLD:
        route = "AUTO_APPROVED"
        route_msg = "KYC auto-approved — high confidence ✅"
    elif confidence >= MANUAL_REVIEW_THRESHOLD:
        route = "FLAGGED"
        route_msg = "KYC passed with flag — medium confidence ⚠️"
    else:
        route = "ESCALATE"
        route_msg = "KYC confidence too low — escalating ❌"

    # Explainability: which checks passed
    checks = {
        "identity_match": confidence >= 75,
        "document_valid": confidence >= 70,
        "liveness_check": confidence >= 80,
        "database_match": confidence >= 85,
    }

    return {
        "kyc_verified": kyc_verified,
        "confidence": confidence,
        "route": route,
        "route_msg": route_msg,
        "checks": checks,
        "aadhaar_verified": bool(aadhaar_suffix and len(aadhaar_suffix) == 4),
        "message": route_msg,
        "agent": "VerificationAgent",
        "rule": "KYC_CONFIDENCE_RULE_001",
    }


def query_kyc_confidence(threshold: int = 90) -> dict:
    """Agent-to-agent interface for UnderwritingAgent."""
    result = verify_kyc()
    return {
        "meets_threshold": result["confidence"] >= threshold,
        "confidence": result["confidence"],
        "kyc_verified": result["kyc_verified"],
        "route": result["route"],
    }
