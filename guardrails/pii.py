import re
from typing import List, Tuple

# Precompiled regex patterns for standard PII entities
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(?:\+1[-.\s]?(?:\(\d{3}\)\s*|\d{3}[-.\s])\d{3}[-.\s]?\d{4}\b|"
    r"\b1[-.\s]?(?:\(\d{3}\)\s*|\d{3}[-.\s])\d{3}[-.\s]?\d{4}\b|"
    r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b|"
    r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b)"
)
VIN_PATTERN = re.compile(r"\b[A-Za-z0-9]{17}\b")


def scrub_pii(text: str) -> Tuple[str, List[str]]:
    """Sanitizes text by redacting PII entities (SSN, VIN, Email, Phone).

    Complies with GLBA and HIPAA standards by replacing sensitive identifiers
    with structured replacement tokens before LLM context ingestion.

    Args:
        text: Unsanitized input string (e.g. claimant statement, notes).

    Returns:
        tuple[str, list[str]]: (sanitized_text, list of scrubbed entity types)
    """
    if not text:
        return "", []

    scrubbed_types: List[str] = []
    sanitized = text

    # 1. Scrub SSN (xxx-xx-xxxx)
    if SSN_PATTERN.search(sanitized):
        sanitized = SSN_PATTERN.sub("[REDACTED_SSN]", sanitized)
        scrubbed_types.append("SSN")

    # 2. Scrub Email (scrub before VIN to avoid matching alphanumeric user/domain as VIN)
    if EMAIL_PATTERN.search(sanitized):
        sanitized = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)
        scrubbed_types.append("EMAIL")

    # 3. Scrub Phone Numbers
    if PHONE_PATTERN.search(sanitized):
        sanitized = PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
        scrubbed_types.append("PHONE")

    # 4. Scrub VIN (17 alphanumeric characters)
    if VIN_PATTERN.search(sanitized):
        sanitized = VIN_PATTERN.sub("[REDACTED_VIN]", sanitized)
        scrubbed_types.append("VIN")

    return sanitized, scrubbed_types
