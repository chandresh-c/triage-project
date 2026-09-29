"""Unit tests for Guidewire ClaimCenter and Document AI integrations."""

import pytest
from integrations.guidewire import get_policy_details, get_claims_history
from integrations.document_ai import parse_claim_document


class TestGuidewireIntegration:
    def test_get_active_policy(self):
        policy = get_policy_details("POL-AUTO-1001")
        assert policy["policy_number"] == "POL-AUTO-1001"
        assert policy["status"] == "ACTIVE"
        assert policy["coverages"]["collision"]["deductible"] == 500
        assert policy["coverages"]["collision"]["active"] is True

    def test_get_lapsed_policy(self):
        policy = get_policy_details("POL-AUTO-3003")
        assert policy["status"] == "LAPSED"
        assert policy["coverages"]["collision"]["active"] is False

    def test_get_clean_claims_history(self):
        history = get_claims_history("POL-AUTO-1001")
        assert history["past_claims_count"] == 0
        assert history["siu_referral_history"] is False
        assert history["fraud_risk_score"] == 0.0

    def test_get_high_risk_fraud_claims_history(self):
        history = get_claims_history("POL-AUTO-4004")
        assert history["siu_referral_history"] is True
        assert history["fraud_risk_score"] > 0.8
        assert "MULTIPLE_TOTAL_LOSS_CLAIMS_IN_FIRST_90_DAYS" in history["risk_flags"]

    def test_fallback_policy_for_unknown_number(self):
        policy = get_policy_details("POL-UNKNOWN-999")
        assert policy["status"] == "ACTIVE"
        assert "collision" in policy["coverages"]


class TestDocumentAIParser:
    def test_parse_repair_estimate(self):
        content = """
        ABC Auto Body Shop
        Front bumper cover replacement: $650.00
        Right headlamp assembly: $450.00
        Paint and labor: $825.50
        Total Estimated Cost: $1,925.50
        Vehicle is drivable.
        """
        parsed = parse_claim_document("repair_estimate", content)
        assert parsed["is_valid"] is True
        assert parsed["extracted_fields"]["total_estimated_amount"] == 1925.50
        assert parsed["extracted_fields"]["is_vehicle_drivable"] is True
        assert parsed["extracted_fields"]["damaged_parts_count"] >= 3

    def test_parse_police_report_with_injuries(self):
        content = """
        Metropolitan Police Traffic Incident Report
        Accident Type: Rear-end collision
        Narrative: Unit 1 struck Unit 2 at intersection. Driver of Unit 2 transported by ambulance to hospital with back injuries.
        Citation issued to Unit 1 for following too closely.
        """
        parsed = parse_claim_document("police_report", content)
        assert parsed["is_valid"] is True
        assert parsed["extracted_fields"]["has_reported_injuries"] is True
        assert parsed["extracted_fields"]["citation_issued"] is True

    def test_parse_police_report_with_racing(self):
        content = "Vehicle was observed participating in an unauthorized speed contest / drag race on public roadway."
        parsed = parse_claim_document("police_report", content)
        assert parsed["extracted_fields"]["racing_or_competition_noted"] is True

    def test_parse_empty_document(self):
        parsed = parse_claim_document("repair_estimate", "   ")
        assert parsed["is_valid"] is False
        assert parsed["confidence_score"] == 0.0
