"""
Auto Insurance Policy Clauses and Standard Provisions.

Curated gold-standard insurance policy contract clauses representing collision,
comprehensive, exclusions, rental reimbursement, and claim filing duties.
"""

from typing import List, Dict, Any

STANDARD_AUTO_POLICY_CLAUSES: List[Dict[str, Any]] = [
    {
        "clause_id": "SEC-COL-101",
        "title": "Section I: Collision Coverage & Deductible",
        "category": "coverage",
        "text": (
            "We will pay for direct, accidental physical damage to your covered auto caused by a collision "
            "with another vehicle, object, or by vehicle overturn. Payment is subject to the applicable collision "
            "deductible specified in the Policy Declarations. We will pay the cost to repair or replace the damaged "
            "property with parts of like kind and quality, minus the deductible."
        )
    },
    {
        "clause_id": "SEC-COMP-201",
        "title": "Section II: Comprehensive (Other Than Collision) Coverage",
        "category": "coverage",
        "text": (
            "We will pay for direct, accidental loss or damage to your covered auto not caused by collision. "
            "Comprehensive losses include, but are not limited to: missiles or falling objects, fire, theft, "
            "larceny, explosion, earthquake, windstorm, hail, flood, malicious mischief, vandalism, riot, contact "
            "with a bird or animal, or glass breakage. Payment is subject to the comprehensive deductible."
        )
    },
    {
        "clause_id": "SEC-EXCL-301",
        "title": "Section III: Exclusion - Racing, Track & Speed Contests",
        "category": "exclusion",
        "text": (
            "Coverage under Section I (Collision) and Section II (Comprehensive) does not apply to any vehicle "
            "operated in, participating in, or practicing for any prearranged, organized, or informal racing contest, "
            "speed competition, drag race, stunt activity, demolition derby, or track day event, whether held on a "
            "closed track, private property, or public highway."
        )
    },
    {
        "clause_id": "SEC-EXCL-302",
        "title": "Section III: Exclusion - Rideshare and Commercial Livery Use",
        "category": "exclusion",
        "text": (
            "Coverage does not apply while the covered auto is being used as a public or livery conveyance, "
            "including carrying persons or property for compensation, or while logged into any transportation network "
            "platform (e.g., Uber, Lyft) or courier delivery service, unless a specific commercial endorsement is active."
        )
    },
    {
        "clause_id": "SEC-EXCL-303",
        "title": "Section III: Exclusion - Intentional Acts and Material Misrepresentation",
        "category": "exclusion",
        "text": (
            "No coverage is provided for any loss, damage, or liability caused intentionally by, or at the direction "
            "of, the named insured or any relative. If the insured conceals, misrepresents, or falsely states any "
            "material fact or circumstance concerning the loss or claim, this policy shall be voidable and coverage denied."
        )
    },
    {
        "clause_id": "SEC-RENT-401",
        "title": "Section IV: Additional Coverages - Rental Reimbursement",
        "category": "endorsement",
        "text": (
            "If Rental Vehicle Reimbursement is purchased and listed on your Declarations, we will reimburse "
            "up to $40.00 per day, up to a maximum of 30 continuous calendar days (maximum $1,200.00), for reasonable "
            "expenses incurred to rent a substitute passenger vehicle while your covered auto is withdrawn from normal "
            "use due to a covered collision or comprehensive loss."
        )
    },
    {
        "clause_id": "SEC-COND-501",
        "title": "Section V: General Conditions - Duties After an Accident or Loss",
        "category": "conditions",
        "text": (
            "In the event of an accident or loss, the insured must: (a) Give prompt written notice of the claim to us; "
            "(b) Protect the vehicle from further damage; (c) Cooperate with our investigation and settlement of the claim; "
            "(d) Submit a copy of the official police report and itemized repair estimate; and (e) Permit inspection and "
            "appraisal of the damaged property prior to repairs being initiated."
        )
    }
]
