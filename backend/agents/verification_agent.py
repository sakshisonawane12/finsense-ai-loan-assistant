"""
verification_agent.py
Deterministic KYC — same Aadhaar suffix always produces same confidence score.
Fixes the double-call agent-to-agent bug: confidence is computed once and passed through.
"""

AUTO_APPROVE_THRESHOLD  = 92
MANUAL_REVIEW_THRESHOLD = 75


def compute_kyc_confidence(aadhaar_suffix: str, retry: bool = False) -> int:
    """
    Deterministic: same suffix → same score every time.
    Uses hash so it's stable across calls — fixes the double-call bug.
    Retry bumps score by 10 points (capped at 99).
    """
    if not aadhaar_suffix or len(aadhaar_suffix) != 4:
        return 60  # clearly low — will escalate

    base = 75 + (abs(hash(aadhaar_suffix)) % 25)   # 75–99
    return min(99, base + (10 if retry else 0))


def verify_kyc(aadhaar_suffix: str = "", retry: bool = False) -> dict:
    """
    Runs KYC verification once. Returns structured result with confidence,
    route, per-check breakdown, and rule code.
    Confidence is stored in state after this call — NOT re-computed later.
    """
    confidence = compute_kyc_confidence(aadhaar_suffix, retry)
    kyc_verified = confidence >= MANUAL_REVIEW_THRESHOLD

    if confidence >= AUTO_APPROVE_THRESHOLD:
        route, route_msg = "AUTO_APPROVED", "KYC auto-approved — high confidence ✅"
    elif confidence >= MANUAL_REVIEW_THRESHOLD:
        route, route_msg = "FLAGGED", "KYC passed with flag — medium confidence ⚠️"
    else:
        route, route_msg = "ESCALATE", "KYC confidence too low — escalating ❌"

    checks = {
        "identity_match": confidence >= 75,
        "document_valid": confidence >= 70,
        "liveness_check": confidence >= 80,
        "database_match": confidence >= 85,
    }

    return {
        "kyc_verified":    kyc_verified,
        "confidence":      confidence,
        "route":           route,
        "route_msg":       route_msg,
        "checks":          checks,
        "aadhaar_verified": len(aadhaar_suffix) == 4,
        "message":         route_msg,
        "agent":           "VerificationAgent",
        "rule":            "KYC_CONFIDENCE_RULE_001",
    }


def query_kyc_confidence(kyc_confidence: int, threshold: int = 90) -> dict:
    """
    Agent-to-agent interface.
    FIXED: accepts the already-computed confidence from state — no second KYC call.
    UnderwritingAgent calls this with the confidence value stored after verify_kyc().
    """
    return {
        "meets_threshold": kyc_confidence >= threshold,
        "confidence":      kyc_confidence,
        "kyc_verified":    kyc_confidence >= MANUAL_REVIEW_THRESHOLD,
    }
