"""
Curated Evaluation Benchmark Scenarios and Synthetic 200+ Generator.

Provides the 6 core enterprise test scenarios and a synthetic generator
for bulk evaluation runs.
"""

from typing import List, Dict, Any
import random

GOLD_SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "SCENARIO-01-SIMPLE-AUTO",
        "name": "Simple Auto Collision",
        "description": "Standard rear-end collision with drivable vehicle, complete documentation, active policy, and zero prior claims.",
        "input": {
            "claim_id": "CLM-GOLD-001",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-05-15",
            "claimant_statement": "I was stopped at a red light when another vehicle tapped my rear bumper. Minor damage.",
            "raw_documents": [
                {
                    "doc_type": "police_report",
                    "content": "Metropolitan Police. Two-vehicle collision at signalized intersection. Unit 2 rear-ended Unit 1. Citation issued to Unit 2 driver. No injuries."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Certified Collision Center. Rear bumper replacement and paint: $1,450.00. Vehicle is drivable."
                }
            ]
        },
        "expected_recommendation": "FAST_TRACK",
        "expected_is_covered": True,
        "expected_human_review": False
    },
    {
        "id": "SCENARIO-02-POLICY-EXCLUSION",
        "name": "Policy Exclusion (Track Racing)",
        "description": "Vehicle crashed during an organized drag race / speed competition, triggering Section III Exclusion.",
        "input": {
            "claim_id": "CLM-GOLD-002",
            "policy_number": "POL-AUTO-2002",
            "incident_date": "2025-06-20",
            "claimant_statement": "Car lost traction and spun into protective barrier during amateur drag racing speed contest.",
            "raw_documents": [
                {
                    "doc_type": "police_report",
                    "content": "County Sheriff. Single vehicle crash at Raceway Park during speed competition. Vehicle sustained structural front-end damage."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Precision Auto Body. Frame straightening, hood, radiator replacement: $9,800.00. Non-drivable."
                }
            ]
        },
        "expected_recommendation": "MANUAL_REVIEW",
        "expected_is_covered": False,
        "expected_exclusion": "SEC-EXCL-301",
        "expected_human_review": True
    },
    {
        "id": "SCENARIO-03-MISSING-DOCS",
        "name": "Missing Required Documentation",
        "description": "Claim filed without mandatory police accident report or itemized repair estimate.",
        "input": {
            "claim_id": "CLM-GOLD-003",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-07-04",
            "claimant_statement": "Someone dented my passenger door in a grocery store parking lot. I do not have a repair estimate or police report yet.",
            "raw_documents": []
        },
        "expected_recommendation": "REQUEST_INFO",
        "expected_is_covered": True,
        "expected_human_review": True
    },
    {
        "id": "SCENARIO-04-SIU-FRAUD",
        "name": "High-Risk Fraud / SIU Referral",
        "description": "Policyholder with history of multiple total loss claims in first 90 days and active SIU referral flags.",
        "input": {
            "claim_id": "CLM-GOLD-004",
            "policy_number": "POL-AUTO-4004",
            "incident_date": "2025-08-10",
            "claimant_statement": "Engine compartment mysteriously caught fire while parked overnight in alleyway.",
            "raw_documents": [
                {
                    "doc_type": "police_report",
                    "content": "Fire Marshal & Police Incident. Unattended vehicle total loss fire. Suspicious accelerant pattern noted."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Total Loss Valuation: $48,000.00."
                }
            ]
        },
        "expected_recommendation": "SIU_FRAUD_INVESTIGATION",
        "expected_human_review": True
    },
    {
        "id": "SCENARIO-05-COVERAGE-QUERY",
        "name": "Coverage Question Grounded in Policy",
        "description": "Inquiry regarding rental reimbursement coverage while vehicle is in the repair shop.",
        "input": {
            "claim_id": "CLM-GOLD-005",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-09-02",
            "claimant_statement": "Will my policy reimburse me for a rental car while my vehicle is being repaired from collision?",
            "raw_documents": [
                {
                    "doc_type": "repair_estimate",
                    "content": "Estimated repair duration: 6 business days. Total cost: $2,100.00."
                },
                {
                    "doc_type": "police_report",
                    "content": "Minor fender bender. No injuries."
                }
            ]
        },
        "expected_recommendation": "FAST_TRACK",
        "expected_is_covered": True,
        "expected_human_review": False
    },
    {
        "id": "SCENARIO-06-AMBIGUOUS-CONFLICT",
        "name": "Ambiguous / Disputed Liability Case",
        "description": "Conflicting statements between parties with disputed traffic light signals.",
        "input": {
            "claim_id": "CLM-GOLD-006",
            "policy_number": "POL-AUTO-1001",
            "incident_date": "2025-09-18",
            "claimant_statement": "Other driver ran the light, but they claim I made an illegal left turn. Conflicting witness statements.",
            "raw_documents": [
                {
                    "doc_type": "claimant_statement",
                    "content": "I had the green arrow. Other driver denies this and claims their light was green."
                },
                {
                    "doc_type": "police_report",
                    "content": "Intersection collision. Both drivers claim green light. Independent witnesses give conflicting accounts. No citation issued."
                },
                {
                    "doc_type": "repair_estimate",
                    "content": "Side quarter panel impact: $3,600.00."
                }
            ]
        },
        "expected_recommendation": "MANUAL_REVIEW",
        "expected_human_review": True
    }
]


def generate_scenario_batch(total_count: int = 200) -> List[Dict[str, Any]]:
    """
    Generate a balanced synthetic batch of claims scenarios simulating enterprise distributions:
    - 40% Simple auto collision (Fast-track)
    - 20% Missing documentation (Request info)
    - 15% Policy exclusion / lapsed coverage (Manual review)
    - 15% High-risk fraud (SIU investigation)
    - 10% Ambiguous liability (Manual review)
    """
    batch = []
    
    # Counts
    n_simple = int(total_count * 0.40)
    n_missing = int(total_count * 0.20)
    n_excl = int(total_count * 0.15)
    n_fraud = int(total_count * 0.15)
    n_ambiguous = total_count - (n_simple + n_missing + n_excl + n_fraud)

    # 1. Simple claims
    for i in range(n_simple):
        cost = round(random.uniform(800.0, 4500.0), 2)
        batch.append({
            "id": f"SYN-SIMPLE-{i+1:03d}",
            "name": f"Synthetic Simple Collision #{i+1}",
            "input": {
                "claim_id": f"CLM-SYN-S-{i+1:03d}",
                "policy_number": "POL-AUTO-1001",
                "incident_date": "2025-05-10",
                "claimant_statement": "Rear bumper tap at intersection signal.",
                "raw_documents": [
                    {"doc_type": "police_report", "content": "Minor rear-end collision. Citation issued to other driver. No injuries."},
                    {"doc_type": "repair_estimate", "content": f"Bumper cover repair: ${cost:,.2f}. Vehicle is drivable."}
                ]
            },
            "expected_recommendation": "FAST_TRACK",
            "expected_human_review": False
        })

    # 2. Missing docs
    for i in range(n_missing):
        batch.append({
            "id": f"SYN-MISSING-{i+1:03d}",
            "name": f"Synthetic Missing Docs #{i+1}",
            "input": {
                "claim_id": f"CLM-SYN-M-{i+1:03d}",
                "policy_number": "POL-AUTO-1001",
                "incident_date": "2025-06-01",
                "claimant_statement": "Vehicle was scratched in driveway. Need claims adjuster to inspect.",
                "raw_documents": []
            },
            "expected_recommendation": "REQUEST_INFO",
            "expected_human_review": True
        })

    # 3. Policy exclusions
    for i in range(n_excl):
        batch.append({
            "id": f"SYN-EXCL-{i+1:03d}",
            "name": f"Synthetic Exclusion #{i+1}",
            "input": {
                "claim_id": f"CLM-SYN-E-{i+1:03d}",
                "policy_number": "POL-AUTO-2002",
                "incident_date": "2025-07-15",
                "claimant_statement": "Vehicle crashed during informal drag racing track event competition.",
                "raw_documents": [
                    {"doc_type": "police_report", "content": "Speed contest crash on private closed course."},
                    {"doc_type": "repair_estimate", "content": "Total front damage: $14,000.00."}
                ]
            },
            "expected_recommendation": "MANUAL_REVIEW",
            "expected_human_review": True
        })

    # 4. SIU Fraud
    for i in range(n_fraud):
        batch.append({
            "id": f"SYN-FRAUD-{i+1:03d}",
            "name": f"Synthetic SIU Fraud #{i+1}",
            "input": {
                "claim_id": f"CLM-SYN-F-{i+1:03d}",
                "policy_number": "POL-AUTO-4004",
                "incident_date": "2025-08-01",
                "claimant_statement": "Total loss fire reported in parking lot.",
                "raw_documents": [
                    {"doc_type": "police_report", "content": "Suspicious total loss arson investigation."},
                    {"doc_type": "repair_estimate", "content": "Total loss: $35,000.00."}
                ]
            },
            "expected_recommendation": "SIU_FRAUD_INVESTIGATION",
            "expected_human_review": True
        })

    # 5. Ambiguous
    for i in range(n_ambiguous):
        batch.append({
            "id": f"SYN-AMBIG-{i+1:03d}",
            "name": f"Synthetic Ambiguous #{i+1}",
            "input": {
                "claim_id": f"CLM-SYN-A-{i+1:03d}",
                "policy_number": "POL-AUTO-1001",
                "incident_date": "2025-09-01",
                "claimant_statement": "Intersection collision with disputed fault and conflicting witness testimonies.",
                "raw_documents": [
                    {"doc_type": "police_report", "content": "Conflicting statements regarding who entered intersection first."},
                    {"doc_type": "repair_estimate", "content": "Front fender repair: $2,800.00."}
                ]
            },
            "expected_recommendation": "MANUAL_REVIEW",
            "expected_human_review": True
        })

    return batch
