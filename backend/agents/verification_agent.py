# agents/verification_agent.py

# ================= CONSTANTS =================
AUTO_APPROVE_THRESHOLD = 92
MANUAL_REVIEW_THRESHOLD = 75


# ================= HELPER =================

def get_kyc_confidence(aadhaar_suffix: str) -> int:
    """
    Deterministic confidence based on Aadhaar suffix
    Ensures consistent results across calls
    """
    if not aadhaar_suffix:
        return 70  # fallback low confidence

    return 75 + (hash(aadhaar_suffix) % 25)  # 75–99 stable


# ================= MAIN =================

def verify_kyc(retry: bool = False, aadhaar_suffix: str = "") -> dict:
    """
    Deterministic KYC system

    Routing:
    ≥92 → Auto approve
    75–91 → Flagged
    <75 → Escalate
    """

    confidence = get_kyc_confidence(aadhaar_suffix)

    # Retry improves confidence
    if retry:
        confidence = max(confidence, 92)

    kyc_verified = confidence >= MANUAL_REVIEW_THRESHOLD

    # Routing logic
    if confidence >= AUTO_APPROVE_THRESHOLD:
        route = "AUTO_APPROVED"
        route_msg = "KYC auto-approved — high confidence ✅"

    elif confidence >= MANUAL_REVIEW_THRESHOLD:
        route = "FLAGGED"
        route_msg = "KYC passed with flag — medium confidence ⚠️"

    else:
        route = "ESCALATE"
        route_msg = "KYC confidence too low — escalating ❌"

    # Explainability checks
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


# ================= AGENT INTERFACE =================

def query_kyc_confidence(threshold: int = 90, aadhaar_suffix: str = "") -> dict:
    """
    Agent-to-agent interface (kept for compatibility)
    """

    result = verify_kyc(aadhaar_suffix=aadhaar_suffix)

    return {
        "meets_threshold": result["confidence"] >= threshold,
        "confidence": result["confidence"],
        "kyc_verified": result["kyc_verified"],
        "route": result["route"],
    }