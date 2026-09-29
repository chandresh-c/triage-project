"""Unit tests for LangGraph state machine, nodes, and routing."""

import pytest
from core.state import TriageState, TriageDecision
from core.graph import build_claims_graph, process_claim


class TestCoreLangGraphWorkflow:
    def test_graph_compilation(self):
        graph = build_claims_graph()
        assert graph is not None

    def test_process_simple_claim_fast_tracks(self):
        claim_input = {
            "claim_id": "CLM-TEST-001",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-05-10",
            "claimant_statement": "I was rear-ended at a red light by another vehicle. My bumper was dented. Contact me at 555-123-4567 or SSN 123-45-6789.",
            "raw_documents": [
                {
                    "doc_type": "repair_estimate",
                    "content": "Front and rear bumper replacement: $1,850.00. Vehicle is drivable."
                },
                {
                    "doc_type": "police_report",
                    "content": "Rear-end collision. Other driver cited for failure to stop. No injuries."
                }
            ]
        }
        result = process_claim(claim_input)
        assert result is not None
        assert "decision" in result
        decision = result["decision"]
        assert isinstance(decision, TriageDecision)
        assert decision.recommendation == "FAST_TRACK"
        assert decision.is_covered is True
        assert result["requires_human_review"] is False
        assert result["route"] == "auto_settlement"
        # Verify PII was redacted from claimant statement
        assert "123-45-6789" not in result["claimant_statement"]
        assert "[REDACTED_SSN]" in result["claimant_statement"]

    def test_process_policy_exclusion_escalates(self):
        claim_input = {
            "claim_id": "CLM-TEST-002",
            "policy_number": "POL-AUTO-2002",
            "incident_date": "2025-06-12",
            "claimant_statement": "Vehicle hit tire wall during high-speed drag racing track event.",
            "raw_documents": [
                {
                    "doc_type": "police_report",
                    "content": "Vehicle crashed during weekend speed competition event on track."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Heavy front frame damage: $12,500.00. Towed from scene."
                }
            ]
        }
        result = process_claim(claim_input)
        decision = result["decision"]
        assert decision.recommendation == "MANUAL_REVIEW"
        assert decision.is_covered is False
        assert "SEC-EXCL-301" in decision.policy_exclusions_identified
        assert result["requires_human_review"] is True
        assert result["route"] == "adjuster_queue"

    def test_process_missing_documents_requests_info(self):
        claim_input = {
            "claim_id": "CLM-TEST-003",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-07-01",
            "claimant_statement": "My car was hit in a parking lot. I do not have a repair estimate yet.",
            "raw_documents": []
        }
        result = process_claim(claim_input)
        decision = result["decision"]
        assert decision.recommendation == "REQUEST_INFO"
        assert len(decision.missing_documents) > 0
        assert "police_report" in decision.missing_documents
        assert "repair_estimate" in decision.missing_documents
        assert result["requires_human_review"] is True
        assert result["route"] == "adjuster_queue"

    def test_process_siu_fraud_escalates(self):
        claim_input = {
            "claim_id": "CLM-TEST-004",
            "policy_number": "POL-AUTO-4004",  # High risk policy
            "incident_date": "2025-08-01",
            "claimant_statement": "Total loss fire in engine bay after minor fender bump.",
            "raw_documents": [
                {
                    "doc_type": "police_report",
                    "content": "Suspicious engine fire after low speed impact."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Total Loss: $45,000.00."
                }
            ]
        }
        result = process_claim(claim_input)
        decision = result["decision"]
        assert decision.recommendation == "SIU_FRAUD_INVESTIGATION"
        assert decision.fraud_risk_score > 0.6
        assert result["requires_human_review"] is True
        assert result["route"] == "adjuster_queue"

    def test_process_conflicting_statements_escalates(self):
        claim_input = {
            "claim_id": "CLM-TEST-005",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-09-01",
            "claimant_statement": "The other driver denies fault. Conflicting statements from both parties.",
            "raw_documents": [
                {
                    "doc_type": "claimant_statement",
                    "content": "Witness claims I was speeding, but I dispute this completely."
                },
                {
                    "doc_type": "police_report",
                    "content": "Both drivers claim green light. Conflicting witness statements."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Side door impact: $3,200.00."
                }
            ]
        }
        result = process_claim(claim_input)
        decision = result["decision"]
        assert decision.recommendation == "MANUAL_REVIEW"
        assert result["requires_human_review"] is True
