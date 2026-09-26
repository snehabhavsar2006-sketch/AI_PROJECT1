"""
csp_validator.py
Constraint Satisfaction Problem (CSP) Validator.
Enforces hard logical constraints on HDC-shortlisted candidate responders:
1. Vehicle Type Compatibility
2. Responder Capacity >= Incident Severity
3. Responder Availability
"""

from environment import COMPATIBILITY_RULES, DISCLAIMERS

def validate_csp_constraints(incident, shortlisted_responders):
    """
    Evaluates HDC-shortlisted responders against hard domain constraints.
    Returns list of dicts with pass/fail validation status and explicit rejection reasons.
    """
    results = []
    inc_type = incident["incident_type"].upper()
    inc_severity = incident["severity"]
    
    allowed_types = COMPATIBILITY_RULES.get(inc_type, [])
    
    for resp in shortlisted_responders:
        resp_id = resp["responder_id"]
        resp_type = resp["type"].lower()
        capacity = resp["capacity"]
        available = bool(resp.get("availability", 1))
        
        rejection_reasons = []
        
        # Constraint 1: Responder Type Compatibility
        if resp_type not in allowed_types:
            allowed_str = ", ".join(allowed_types)
            rejection_reasons.append(f"Incompatible type '{resp_type}' (Requires: {allowed_str})")
            
        # Constraint 2: Capacity >= Severity
        if capacity < inc_severity:
            rejection_reasons.append(f"Insufficient capacity ({capacity} < {inc_severity})")
            
        # Constraint 3: Availability
        if not available:
            rejection_reasons.append("Responder unavailable (currently assigned)")
            
        is_valid = (len(rejection_reasons) == 0)
        rejection_str = "; ".join(rejection_reasons) if rejection_reasons else "All constraints satisfied"
        
        results.append({
            "responder_id": resp_id,
            "type": resp_type,
            "availability": available,
            "capacity": capacity,
            "incident_severity": inc_severity,
            "csp_valid": is_valid,
            "rejection_reason": rejection_str,
            "hdc_similarity": resp.get("hdc_similarity", 0.0)
        })
        
    return results
