"""
explainer.py
Generates human-readable, plain-language explainability rationales for every stage of emergency dispatch.
Designed for clear explanation during academic viva presentations without emojis.
"""

def explain_incident_priority(incident, rank, total_queue_size):
    """Generates priority queue rationale."""
    urgency = incident.get("urgency_score", (incident["severity"] * 10))
    return (
        f"Incident {incident['incident_id']} ({incident['incident_type']}) was prioritized as Rank #{rank} "
        f"out of {total_queue_size} pending emergencies because it has the highest Urgency Score of {urgency} "
        f"(Severity: {incident['severity']}, Waiting Time: {incident.get('waiting_time_min', 0)} mins)."
    )

def explain_hdc_screening(hdc_results):
    """Generates HDC candidate screening rationale."""
    shortlisted = [r for r in hdc_results if r["shortlisted"]]
    shortlisted_ids = ", ".join([r["responder_id"] for r in shortlisted]) if shortlisted else "None"
    
    explanation = [
        f"Hyperdimensional Computing (HDC) screened all {len(hdc_results)} candidates in D=10,000 bipolar vector space.",
        f"Shortlisted {len(shortlisted)} candidate(s): {shortlisted_ids}.",
        "Individual HDC Similarity Scores:"
    ]
    for r in hdc_results:
        status = "[SHORTLISTED]" if r["shortlisted"] else "[FILTERED OUT]"
        explanation.append(f"  - {r['responder_id']} ({r['type']}): Similarity = {r['hdc_similarity']:.4f} ({status})")
        
    return "\n".join(explanation)

def explain_csp_validation(csp_results):
    """Generates CSP constraint validation rationale."""
    valid = [r for r in csp_results if r["csp_valid"]]
    invalid = [r for r in csp_results if not r["csp_valid"]]
    
    explanation = [
        f"Constraint Satisfaction Problem (CSP) validated hard logical rules for {len(csp_results)} shortlisted candidate(s).",
        f"CSP Valid Candidates ({len(valid)}): {', '.join([r['responder_id'] for r in valid]) if valid else 'None'}."
    ]
    
    if invalid:
        explanation.append("Rejection Rationales:")
        for r in invalid:
            explanation.append(f"  - {r['responder_id']} ({r['type']}): REJECTED -- {r['rejection_reason']}")
            
    return "\n".join(explanation)

def explain_astar_routing(routing_results, selected_responder_id):
    """Generates A* route planning rationale."""
    explanation = [
        "A* Pathfinding evaluated route costs on the 10x10 research grid using Manhattan Distance heuristic h(x,y) = |x1-x2| + |y1-y2|.",
        "Candidate Route Comparisons:"
    ]
    for r in routing_results:
        is_selected = (r["responder_id"] == selected_responder_id)
        tag = "[SELECTED - Lowest Route Cost]" if is_selected else "[Alternative Valid Route]"
        explanation.append(
            f"  - {r['responder_id']} ({r['type']}): Distance = {r['distance']} grid cells, Route Cost = {r['route_cost']:.1f} ({tag})"
        )
    return "\n".join(explanation)

def explain_final_dispatch_decision(incident, selected_responder, dispatch_details):
    """Generates final overall explainability summary."""
    if not selected_responder:
        return (
            f"NO RESPONDER ASSIGNED for Incident {incident['incident_id']} ({incident['incident_type']}).\n"
            "Reason: No HDC-shortlisted responder satisfied all hard CSP constraints (type compatibility, capacity, availability)."
        )
        
    return (
        f"RESPONDER {selected_responder['responder_id']} ({selected_responder['type']}) DISPATCHED to {incident['location_text']}.\n\n"
        f"Selection Rationale:\n"
        f"1. Type Compatible: Vehicle type matches incident requirement ({incident['incident_type']}).\n"
        f"2. Sufficient Capacity: Vehicle capacity ({selected_responder['capacity']}) >= Incident severity ({incident['severity']}).\n"
        f"3. Available: Vehicle is free and unassigned in database.\n"
        f"4. Optimal Route: Achieved lowest calculated A* route cost ({dispatch_details['route_cost']:.1f}) on research grid."
    )
