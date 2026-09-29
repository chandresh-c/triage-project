"""Unit tests for Policy Retrieval RAG subsystem."""

import pytest
from retrieval.store import PolicyVectorStore


class TestPolicyRetrieval:
    @pytest.fixture
    def store(self):
        return PolicyVectorStore()

    def test_retrieve_collision_clause(self, store):
        query = "Vehicle suffered rear bumper collision damage from another car"
        results = store.search(query, top_k=2)
        assert len(results) > 0
        clause_ids = [r["clause_id"] for r in results]
        assert "SEC-COL-101" in clause_ids

    def test_retrieve_racing_exclusion(self, store):
        query = "Claimant was participating in an illegal street racing speed contest"
        results = store.search(query, top_k=2)
        assert len(results) > 0
        top_result = results[0]
        assert top_result["clause_id"] == "SEC-EXCL-301"
        assert top_result["category"] == "exclusion"
        assert "racing" in top_result["text"].lower()

    def test_retrieve_rideshare_exclusion(self, store):
        query = "Driver was transporting passengers for Uber / Lyft delivery rideshare"
        results = store.search(query, top_k=2)
        assert len(results) > 0
        top_result = results[0]
        assert top_result["clause_id"] == "SEC-EXCL-302"
        assert "livery" in top_result["text"].lower() or "uber" in top_result["text"].lower()

    def test_retrieve_rental_car_coverage(self, store):
        query = "Will insurance pay for rental vehicle reimbursement while car is in the repair shop?"
        results = store.search(query, top_k=2)
        assert len(results) > 0
        clause_ids = [r["clause_id"] for r in results]
        assert "SEC-RENT-401" in clause_ids

    def test_retrieve_duties_after_accident(self, store):
        query = "Need police report and repair estimate documentation duties"
        results = store.search(query, top_k=2)
        assert len(results) > 0
        clause_ids = [r["clause_id"] for r in results]
        assert "SEC-COND-501" in clause_ids
