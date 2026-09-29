"""
Enterprise Integration: Document AI Parser.

Simulates Azure AI Document Intelligence / AWS Textract parsing structured
key-value pairs and tables from police reports, repair estimates, and FNOL forms.
"""

from typing import Dict, Any, List, Optional
import re


def parse_claim_document(doc_type: str, content: str) -> Dict[str, Any]:
    """
    Parse an uploaded insurance document and extract normalized fields.
    
    Args:
        doc_type: 'police_report', 'repair_estimate', 'claimant_statement', or 'acord_fnol'
        content: Raw text or OCR string of the document.
        
    Returns:
        Structured dictionary containing extracted key entities, detected damage,
        estimated costs, and extraction confidence score.
    """
    doc_type_normalized = doc_type.lower().strip()
    result: Dict[str, Any] = {
        "doc_type": doc_type_normalized,
        "is_valid": True,
        "confidence_score": 0.95,
        "extracted_fields": {},
        "raw_text_length": len(content)
    }

    if not content or not content.strip():
        return {
            "doc_type": doc_type_normalized,
            "is_valid": False,
            "confidence_score": 0.0,
            "extracted_fields": {},
            "error": "Document is empty or unreadable"
        }

    # Extract common monetary amounts ($X,XXX.XX)
    amounts = re.findall(r"\$\s?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)", content)
    float_amounts = []
    for a in amounts:
        try:
            float_amounts.append(float(a.replace(",", "")))
        except ValueError:
            pass

    if doc_type_normalized == "repair_estimate":
        total_estimate = max(float_amounts) if float_amounts else 0.0
        # Check for drivable status
        drivable = "non-drivable" not in content.lower() and "towed" not in content.lower()
        parts_labor = [line.strip() for line in content.splitlines() if any(k in line.lower() for k in ["bumper", "fender", "door", "glass", "paint", "labor", "replace", "repair", "lamp", "light", "hood", "panel", "assembly"])]
        
        result["extracted_fields"] = {
            "total_estimated_amount": total_estimate,
            "is_vehicle_drivable": drivable,
            "damaged_parts_count": len(parts_labor),
            "line_items": parts_labor[:10]
        }

    elif doc_type_normalized == "police_report":
        # Check for citation, fault, injuries
        has_injuries = any(k in content.lower() for k in ["injury", "injured", "hospital", "ems", "paramedic", "ambulance", "fatal"])
        citation_issued = "citation" in content.lower() or "cited" in content.lower() or "ticket" in content.lower()
        
        # Check for specific racing / illegal behavior keywords
        racing_mentioned = any(k in content.lower() for k in ["racing", "track event", "drag race", "speed contest"])
        
        result["extracted_fields"] = {
            "has_reported_injuries": has_injuries,
            "citation_issued": citation_issued,
            "racing_or_competition_noted": racing_mentioned,
            "accident_type": "rear_end" if "rear-end" in content.lower() or "rear end" in content.lower() else "collision"
        }

    elif doc_type_normalized == "claimant_statement":
        result["extracted_fields"] = {
            "narrative_summary": content[:300],
            "mentions_other_party": any(k in content.lower() for k in ["other driver", "other vehicle", "third party", "truck"]),
            "disputed_liability": any(k in content.lower() for k in ["dispute", "denies", "claims i was at fault", "conflicting"])
        }

    else:
        # Generic document
        result["extracted_fields"] = {
            "amounts_detected": float_amounts,
            "snippet": content[:200]
        }

    return result
