import re

# Adversarial prompt injection patterns targeting LLM instruction override and jailbreaks
INJECTION_PATTERNS = [
    re.compile(
        r"\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above|system)\s+instructions?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bbypass\s+(?:all\s+)?(?:previous|prior|above|system|safety|security)\s+(?:instructions?|checks?|rules?|guardrails?)",
        re.IGNORECASE,
    ),
    re.compile(r"\bsystem\s+override\b", re.IGNORECASE),
    re.compile(r"\badmin(?:istrator)?\s+override\b", re.IGNORECASE),
    re.compile(r"\byou\s+are\s+now\s+in\s+dan\s+mode\b", re.IGNORECASE),
    re.compile(r"\bdan\s+mode\b", re.IGNORECASE),
    re.compile(r"\bdeveloper\s+mode\b", re.IGNORECASE),
    re.compile(r"\bjailbreak\b", re.IGNORECASE),
    re.compile(r"\bdo\s+anything\s+now\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\s+(?:an?\s+)?unrestricted\b", re.IGNORECASE),
    re.compile(
        r"\b(?:reveal|print|output|show|display)\s+(?:the\s+)?(?:system\s+)?prompt\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bnew\s+instructions?\s*:", re.IGNORECASE),
    re.compile(r"\binstruction\s+override\b", re.IGNORECASE),
    re.compile(r"\balways\s+approve(?:\s+this)?\s+claim\b", re.IGNORECASE),
    re.compile(r"\bset\s+status\s+to\s+(?:fast_track|approved)\b", re.IGNORECASE),
    re.compile(r"\boverride\s+(?:coverage|fraud|decision|policy|limits?)\b", re.IGNORECASE),
]


def detect_prompt_injection(text: str) -> bool:
    """Detects adversarial jailbreak or prompt injection attempts in untrusted text.

    Args:
        text: Untrusted input string (e.g. claimant statement, uploaded notes).

    Returns:
        bool: True if an adversarial injection pattern is detected, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False

    for pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return True

    return False


def fence_untrusted_input(text: str, tag: str = "untrusted_document") -> str:
    """Encloses untrusted inputs in XML boundary tags and sanitizes internal delimiter tags.

    Prevents prompt escaping and delimiter injection attacks by escaping inner
    matching tags before enclosing in boundary tags.

    Args:
        text: Untrusted text from claimant, OCR, or third-party documents.
        tag: Outer XML tag delimiter name (defaults to 'untrusted_document').

    Returns:
        str: Fenced and sanitized string ready for prompt template interpolation.
    """
    if text is None:
        text = ""

    # Neutralize any attempts to close or reopen the delimiter tag internally
    sanitized = text.replace(f"</{tag}>", f"&lt;/{tag}&gt;").replace(f"<{tag}>", f"&lt;{tag}&gt;")
    return f"<{tag}>\n{sanitized}\n</{tag}>"
