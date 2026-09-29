"""
Enterprise Integration: Mock Guidewire ClaimCenter REST API.

Provides policy validation, coverage verification, and historical claims retrieval
simulating enterprise core insurance databases (e.g. Guidewire ClaimCenter / PolicyCenter).
"""

from typing import Dict, Any, Optional
from datetime import datetime, date

# Mock Guidewire Policy Database
MOCK_POLICIES: Dict[str, Dict[str, Any]] = {
    "POL-AUTO-1001": {
        "policy_number": "POL-AUTO-1001",
        "policyholder_name": "Jane Doe",
        "status": "ACTIVE",
        "effective_date": "2025-01-01",
        "expiration_date": "2026-01-01",
        "vehicle": {
            "year": 2022,
            "make": "Honda",
            "model": "Civic",
            "vin": "1HGCR2F83NA000000"
        },
        "coverages": {
            "collision": {"limit": 50000, "deductible": 500, "active": True},
            "comprehensive": {"limit": 50000, "deductible": 250, "active": True},
            "property_damage_liability": {"limit": 100000, "deductible": 0, "active": True},
            "bodily_injury_liability": {"limit": 300000, "deductible": 0, "active": True},
            "rental_reimbursement": {"limit_per_day": 40, "max_days": 30, "active": True}
        }
    },
    "POL-AUTO-2002": {
        "policy_number": "POL-AUTO-2002",
        "policyholder_name": "Marcus Vance",
        "status": "ACTIVE",
        "effective_date": "2025-03-01",
        "expiration_date": "2026-03-01",
        "vehicle": {
            "year": 2023,
            "make": "Ford",
            "model": "Mustang GT",
            "vin": "1FA6P8CF5N5000000"
        },
        "coverages": {
            "collision": {"limit": 75000, "deductible": 1000, "active": True},
            "comprehensive": {"limit": 75000, "deductible": 500, "active": True},
            "property_damage_liability": {"limit": 100000, "deductible": 0, "active": True}
        }
    },
    "POL-AUTO-3003": {
        "policy_number": "POL-AUTO-3003",
        "policyholder_name": "Sarah Jenkins",
        "status": "LAPSED",
        "effective_date": "2024-01-01",
        "expiration_date": "2025-01-01",
        "cancellation_reason": "Non-payment of premium",
        "vehicle": {
            "year": 2019,
            "make": "Toyota",
            "model": "Camry",
            "vin": "4T1B11HK5KU000000"
        },
        "coverages": {
            "collision": {"limit": 30000, "deductible": 500, "active": False},
            "comprehensive": {"limit": 30000, "deductible": 500, "active": False}
        }
    },
    "POL-AUTO-4004": {
        "policy_number": "POL-AUTO-4004",
        "policyholder_name": "Arthur Pendelton",
        "status": "ACTIVE",
        "effective_date": "2025-06-01",
        "expiration_date": "2026-06-01",
        "vehicle": {
            "year": 2024,
            "make": "BMW",
            "model": "M3",
            "vin": "WBS33AY08P0000000"
        },
        "coverages": {
            "collision": {"limit": 90000, "deductible": 1000, "active": True},
            "comprehensive": {"limit": 90000, "deductible": 1000, "active": True}
        }
    }
}

# Mock Guidewire Claims History
MOCK_CLAIMS_HISTORY: Dict[str, Dict[str, Any]] = {
    "POL-AUTO-1001": {
        "policy_number": "POL-AUTO-1001",
        "tenure_years": 4.5,
        "past_claims_count": 0,
        "past_claims": [],
        "siu_referral_history": False,
        "fraud_risk_score": 0.0,
        "notes": "Preferred tier customer. Clean claim record."
    },
    "POL-AUTO-2002": {
        "policy_number": "POL-AUTO-2002",
        "tenure_years": 1.2,
        "past_claims_count": 1,
        "past_claims": [
            {
                "claim_id": "CLM-2024-8812",
                "incident_date": "2024-08-15",
                "loss_type": "Windshield Glass",
                "amount_paid": 450.00,
                "status": "CLOSED"
            }
        ],
        "siu_referral_history": False,
        "fraud_risk_score": 0.1,
        "notes": "Standard auto risk."
    },
    "POL-AUTO-3003": {
        "policy_number": "POL-AUTO-3003",
        "tenure_years": 0.5,
        "past_claims_count": 0,
        "past_claims": [],
        "siu_referral_history": False,
        "fraud_risk_score": 0.0,
        "notes": "Policy lapsed."
    },
    "POL-AUTO-4004": {
        "policy_number": "POL-AUTO-4004",
        "tenure_years": 0.2,
        "past_claims_count": 3,
        "past_claims": [
            {
                "claim_id": "CLM-2025-1102",
                "incident_date": "2025-06-15",
                "loss_type": "Total Loss Fire",
                "amount_paid": 42000.00,
                "status": "INVESTIGATED"
            },
            {
                "claim_id": "CLM-2025-3391",
                "incident_date": "2025-07-28",
                "loss_type": "Theft of Parts",
                "amount_paid": 8500.00,
                "status": "CLOSED"
            }
        ],
        "siu_referral_history": True,
        "fraud_risk_score": 0.92,
        "risk_flags": [
            "MULTIPLE_TOTAL_LOSS_CLAIMS_IN_FIRST_90_DAYS",
            "PRIOR_SIU_INVESTIGATION",
            "HIGH_FREQUENCY_LOSS"
        ],
        "notes": "HIGH RISK: Pattern matches staged accident syndicates. Mandatory SIU referral."
    }
}


def get_policy_details(policy_number: str) -> Dict[str, Any]:
    """Retrieve policy terms, active coverages, limits, and vehicle specifications from Guidewire."""
    if policy_number in MOCK_POLICIES:
        return MOCK_POLICIES[policy_number]
    
    # Generic fallback policy for dynamic tests
    return {
        "policy_number": policy_number,
        "policyholder_name": "Standard Insured",
        "status": "ACTIVE",
        "effective_date": "2025-01-01",
        "expiration_date": "2026-01-01",
        "vehicle": {"year": 2021, "make": "General", "model": "Sedan", "vin": "1G1NE52T761000000"},
        "coverages": {
            "collision": {"limit": 50000, "deductible": 500, "active": True},
            "comprehensive": {"limit": 50000, "deductible": 500, "active": True}
        }
    }


def get_claims_history(policy_number: str) -> Dict[str, Any]:
    """Retrieve historical claims, prior losses, and SIU fraud risk indicators from Guidewire."""
    if policy_number in MOCK_CLAIMS_HISTORY:
        return MOCK_CLAIMS_HISTORY[policy_number]
    
    return {
        "policy_number": policy_number,
        "tenure_years": 2.0,
        "past_claims_count": 0,
        "past_claims": [],
        "siu_referral_history": False,
        "fraud_risk_score": 0.0,
        "notes": "Standard account history."
    }
