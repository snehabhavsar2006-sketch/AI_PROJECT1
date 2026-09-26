"""
responder_manager.py
Manages responder statuses, real-world addresses, availability locks, and database updates.
"""

import database as db

def get_all_responders():
    """Retrieves all registered responders from SQLite."""
    return db.get_responders()

def get_available_responders():
    """Retrieves only available responders from SQLite."""
    return db.get_available_responders()

def assign_responder_to_incident(responder_id, incident_id):
    """
    Locks responder availability upon dispatch assignment:
    - availability becomes 0 (FALSE)
    - status becomes 'ASSIGNED'
    - current_assignment becomes incident_id
    """
    db.update_responder_status(
        responder_id=responder_id,
        availability=0,
        status="ASSIGNED",
        current_assignment=incident_id
    )

def release_responder(responder_id):
    """Releases responder back to AVAILABLE state."""
    db.update_responder_status(
        responder_id=responder_id,
        availability=1,
        status="AVAILABLE",
        current_assignment=None
    )

def update_location(responder_id, new_location_text, new_lat, new_lon):
    """Updates physical location address and coordinates for a responder."""
    db.update_responder_location(responder_id, new_location_text, new_lat, new_lon)
