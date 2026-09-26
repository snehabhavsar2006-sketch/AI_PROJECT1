"""
replanner.py
Dynamic Re-planning Engine.
Handles real-time incident updates, responder dropouts, or route blockages.
Reruns HDC, CSP, and A* pipeline to select replacement responders and records changes in `route_updates`.
"""

from datetime import datetime
import database as db

def execute_dynamic_replanning(incident_id, trigger_reason, additional_obstacles=None):
    """
    Triggers dynamic re-planning for an active incident:
    1. Fetches current dispatch and active responder.
    2. Invalidates current responder (e.g., set availability = 0 or handles blockage).
    3. Re-runs dispatch pipeline for incident.
    4. Records transition details into `route_updates` table.
    """
    from coordinator import process_single_incident
    
    incident = db.get_incident(incident_id)
    if not incident:
        return {"success": False, "error": f"Incident {incident_id} not found."}
        
    # Get current dispatch
    history = db.get_dispatch_history()
    current_dispatch = next((d for d in history if d["incident_id"] == incident_id and d["status"] == "DISPATCHED"), None)
    
    old_responder_id = current_dispatch["responder_id"] if current_dispatch else "None"
    old_route = current_dispatch["route"] if current_dispatch else ""
    old_cost = current_dispatch["route_cost"] if current_dispatch else 0.0
    
    # Execute trigger handling
    if trigger_reason == "RESPONDER_UNAVAILABLE" and old_responder_id != "None":
        # Mark old responder unavailable
        db.update_responder_status(old_responder_id, availability=0, status="UNAVAILABLE", current_assignment=None)
        
    # Re-run dispatch pipeline for the incident
    new_result = process_single_incident(incident_id, force_obstacles=additional_obstacles)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    update_id = f"UPD-{int(datetime.now().timestamp())}"
    
    new_responder = new_result.get("selected_responder")
    new_responder_id = new_responder["responder_id"] if new_responder else "NO_RESPONDER"
    new_route = str(new_result.get("selected_path", []))
    new_cost = new_result.get("selected_cost", 0.0)
    
    # Save update to database `route_updates` table (Section 22 Specification)
    db.save_route_update(
        update_id=update_id,
        incident_id=incident_id,
        old_route=old_route,
        new_route=new_route,
        reason=f"{trigger_reason}: Old Responder {old_responder_id} failed or blocked.",
        old_cost=old_cost,
        new_cost=new_cost,
        timestamp=now_str
    )
    
    return {
        "success": True,
        "update_id": update_id,
        "incident_id": incident_id,
        "trigger_reason": trigger_reason,
        "old_responder_id": old_responder_id,
        "new_responder_id": new_responder_id,
        "old_cost": old_cost,
        "new_cost": new_cost,
        "old_route": old_route,
        "new_route": new_route,
        "timestamp": now_str,
        "pipeline_result": new_result
    }
