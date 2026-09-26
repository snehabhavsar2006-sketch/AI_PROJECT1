"""
coordinator.py
Master Pipeline Coordinator.
Chains: Incident Queue -> HDC Candidate Screening -> CSP Constraint Validation -> A* Route Planning -> Selection -> DB Persistence.
"""

from datetime import datetime
import database as db
from incident_detector import rank_emergency_queue
from hdc_screener import screener
from csp_validator import validate_csp_constraints
from astar_router import astar_search, DEMO_GRID_LOCATIONS, DEFAULT_OBSTACLES
import responder_manager as rm
import explainer

def get_prioritized_incident_queue():
    """Fetches all PENDING incidents and ranks them by Urgency Score."""
    pending = db.get_incidents(status="PENDING")
    if not pending:
        # If no PENDING incidents, return all incidents ordered by priority
        pending = db.get_incidents()
    ranked_queue = rank_emergency_queue(pending)
    return ranked_queue

def process_single_incident(incident_id, force_obstacles=None):
    """
    Executes full 5-stage dispatch pipeline for a single target incident:
    1. Stage A: Incident Priority
    2. Stage B: HDC Candidate Screening (all responders)
    3. Stage C: CSP Constraint Validation (shortlisted responders)
    4. Stage D: A* Route Planning (CSP valid responders)
    5. Stage E: Responder Selection & DB Persistence
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    incident = db.get_incident(incident_id)
    if not incident:
        return {"error": f"Incident {incident_id} not found."}
        
    obstacles = force_obstacles if force_obstacles is not None else DEFAULT_OBSTACLES
    inc_grid_pos = DEMO_GRID_LOCATIONS.get(incident_id, (8, 8))
    
    # Fetch available responders
    all_responders = rm.get_all_responders()
    
    # -------------------------------------------------------------
    # STAGE B: HDC SCREENING (Section 14 Specification)
    # -------------------------------------------------------------
    hdc_results = screener.screen_responders(incident, all_responders)
    shortlisted_candidates = [r for r in hdc_results if r["shortlisted"]]
    
    # -------------------------------------------------------------
    # STAGE C: CSP VALIDATION (Section 15 Specification)
    # -------------------------------------------------------------
    csp_results = validate_csp_constraints(incident, shortlisted_candidates)
    valid_csp_candidates = [r for r in csp_results if r["csp_valid"]]
    
    # -------------------------------------------------------------
    # STAGE D: A* ROUTE PLANNING (Section 16 Specification)
    # -------------------------------------------------------------
    routing_evaluations = []
    selected_responder = None
    selected_path = []
    lowest_cost = float('inf')
    best_routing_res = None
    
    for c_info in valid_csp_candidates:
        r_id = c_info["responder_id"]
        r_pos = DEMO_GRID_LOCATIONS.get(r_id, (0, 0))
        
        a_res = astar_search(r_pos, inc_grid_pos, obstacles=obstacles)
        
        eval_item = {
            "responder_id": r_id,
            "type": c_info["type"],
            "capacity": c_info["capacity"],
            "success": a_res["success"],
            "distance": a_res["distance"],
            "route_cost": a_res["route_cost"],
            "path": a_res["path"],
            "eta_mins": round(a_res["distance"] * 1.5, 1)  # Estimated ETA for simulation
        }
        routing_evaluations.append(eval_item)
        
        if a_res["success"] and a_res["route_cost"] < lowest_cost:
            lowest_cost = a_res["route_cost"]
            selected_responder = c_info
            selected_path = a_res["path"]
            best_routing_res = eval_item
            
    # -------------------------------------------------------------
    # STAGE E: SELECTION & SQLITE PERSISTENCE
    # -------------------------------------------------------------
    # Clear previous processing results for this incident to avoid duplicate clutter
    conn = db.get_connection()
    conn.cursor().execute("DELETE FROM processing_results WHERE incident_id = ?", (incident_id,))
    conn.commit()
    conn.close()
    
    # Save processing results into database table `processing_results`
    for h_res in hdc_results:
        r_id = h_res["responder_id"]
        c_res = next((c for c in csp_results if c["responder_id"] == r_id), None)
        a_res = next((a for a in routing_evaluations if a["responder_id"] == r_id), None)
        
        is_shortlisted = h_res["shortlisted"]
        is_csp_valid = c_res["csp_valid"] if c_res else False
        rej_reason = c_res["rejection_reason"] if c_res else ("Filtered by HDC screening" if not is_shortlisted else "Failed CSP")
        
        r_cost = a_res["route_cost"] if a_res else None
        r_dist = a_res["distance"] if a_res else None
        r_eta = a_res["eta_mins"] if a_res else None
        is_selected = (selected_responder and r_id == selected_responder["responder_id"])
        
        proc_id = f"PROC-{incident_id}-{r_id}"
        db.save_processing_result(
            processing_id=proc_id,
            incident_id=incident_id,
            responder_id=r_id,
            hdc_similarity=h_res["hdc_similarity"],
            shortlisted=is_shortlisted,
            csp_valid=is_csp_valid,
            rejection_reason=rej_reason,
            route_cost=r_cost,
            distance=r_dist,
            eta=r_eta,
            selected=is_selected,
            timestamp=now_str
        )
        
    dispatch_record = None
    if selected_responder and best_routing_res:
        resp_id = selected_responder["responder_id"]
        dispatch_id = f"DISP-{incident_id}-{resp_id}"
        
        # Save dispatch record in `dispatches`
        db.create_dispatch(
            dispatch_id=dispatch_id,
            incident_id=incident_id,
            responder_id=resp_id,
            assigned_at=now_str,
            route=str(selected_path),
            route_cost=best_routing_res["route_cost"],
            distance=best_routing_res["distance"],
            eta=best_routing_res["eta_mins"],
            status="DISPATCHED"
        )
        
        # Update responder status in database (Section 21 Specification)
        rm.assign_responder_to_incident(resp_id, incident_id)
        
        # Update incident status
        db.update_incident_status(incident_id, "DISPATCHED")
        
        dispatch_record = {
            "dispatch_id": dispatch_id,
            "responder_id": resp_id,
            "assigned_at": now_str,
            "route_cost": best_routing_res["route_cost"],
            "distance": best_routing_res["distance"],
            "eta": best_routing_res["eta_mins"]
        }
        
    # Generate explanations
    exp_hdc = explainer.explain_hdc_screening(hdc_results)
    exp_csp = explainer.explain_csp_validation(csp_results)
    exp_astar = explainer.explain_astar_routing(routing_evaluations, selected_responder["responder_id"] if selected_responder else None)
    exp_final = explainer.explain_final_dispatch_decision(incident, selected_responder, dispatch_record if dispatch_record else {})
    
    return {
        "incident": incident,
        "incident_pos": inc_grid_pos,
        "hdc_results": hdc_results,
        "shortlisted_candidates": shortlisted_candidates,
        "csp_results": csp_results,
        "valid_csp_candidates": valid_csp_candidates,
        "routing_evaluations": routing_evaluations,
        "selected_responder": selected_responder,
        "selected_path": selected_path,
        "selected_cost": lowest_cost,
        "dispatch_record": dispatch_record,
        "obstacles": obstacles,
        "explanations": {
            "hdc": exp_hdc,
            "csp": exp_csp,
            "astar": exp_astar,
            "final": exp_final
        }
    }
