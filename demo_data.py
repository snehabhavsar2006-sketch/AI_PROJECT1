"""
demo_data.py
Seeds the SQLite database with default emergency incidents, messages, and responders.
Ensures persistent demo state (prevents duplicate insertion on system restarts).
"""

from datetime import datetime
import database as db

def seed_demo_data_if_empty():
    """Inserts default demo records if the database tables are currently empty."""
    db.init_database()
    
    # Check if incidents table already has records
    existing_incidents = db.get_incidents()
    if len(existing_incidents) > 0:
        return  # Database already seeded
        
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. Demo Incidents (Section 5 Specification)
    demo_incidents = [
        {
            "incident_id": "INC-001",
            "incident_type": "FIRE",
            "original_message": "Fire reported near NMIMS Shirpur campus building.",
            "location_text": "NMIMS Shirpur",
            "latitude": 21.3575,
            "longitude": 74.8842,
            "severity": 5,
            "timestamp": now_str,
            "status": "PENDING",
            "source": "DEMO SIMULATION"
        },
        {
            "incident_id": "INC-002",
            "incident_type": "ACCIDENT",
            "original_message": "Vehicle accident reported on Shirpur Highway near main gate.",
            "location_text": "Shirpur Highway",
            "latitude": 21.3510,
            "longitude": 74.8790,
            "severity": 3,
            "timestamp": now_str,
            "status": "PENDING",
            "source": "DEMO SIMULATION"
        },
        {
            "incident_id": "INC-003",
            "incident_type": "MEDICAL",
            "original_message": "Medical emergency reported at Shirpur Central Market.",
            "location_text": "Shirpur Central Market",
            "latitude": 21.3480,
            "longitude": 74.8815,
            "severity": 2,
            "timestamp": now_str,
            "status": "PENDING",
            "source": "DEMO SIMULATION"
        }
    ]
    
    for inc in demo_incidents:
        db.create_incident(
            incident_id=inc["incident_id"],
            incident_type=inc["incident_type"],
            original_message=inc["original_message"],
            location_text=inc["location_text"],
            latitude=inc["latitude"],
            longitude=inc["longitude"],
            severity=inc["severity"],
            timestamp=inc["timestamp"],
            status=inc["status"],
            source=inc["source"]
        )
        
        # Also seed corresponding message into messages table
        msg_id = f"MSG-{inc['incident_id']}"
        db.add_message(
            message_id=msg_id,
            incident_id=inc["incident_id"],
            message_text=inc["original_message"],
            timestamp=inc["timestamp"],
            source=inc["source"]
        )
        
    # 2. Demo Responders (Section 6 Specification: Unique addresses & locations)
    demo_responders = [
        {
            "responder_id": "RESP-001",
            "type": "ambulance",
            "location_text": "Shirpur Station Road (Location A)",
            "latitude": 21.3501,
            "longitude": 74.8801,
            "capacity": 3,
            "availability": 1,
            "status": "AVAILABLE",
            "current_assignment": None
        },
        {
            "responder_id": "RESP-002",
            "type": "fire_truck",
            "location_text": "Shirpur Industrial Zone (Location B)",
            "latitude": 21.3550,
            "longitude": 74.8850,
            "capacity": 6,
            "availability": 1,
            "status": "AVAILABLE",
            "current_assignment": None
        },
        {
            "responder_id": "RESP-003",
            "type": "fire_truck",
            "location_text": "Shirpur Substation Depot (Location C)",
            "latitude": 21.3600,
            "longitude": 74.8900,
            "capacity": 4,
            "availability": 1,
            "status": "AVAILABLE",
            "current_assignment": None
        },
        {
            "responder_id": "RESP-004",
            "type": "ambulance",
            "location_text": "Shirpur Hospital Bay (Location D)",
            "latitude": 21.3450,
            "longitude": 74.8750,
            "capacity": 2,
            "availability": 1,
            "status": "AVAILABLE",
            "current_assignment": None
        },
        {
            "responder_id": "RESP-005",
            "type": "police",
            "location_text": "Shirpur Police HQ (Location E)",
            "latitude": 21.3520,
            "longitude": 74.8820,
            "capacity": 5,
            "availability": 1,
            "status": "AVAILABLE",
            "current_assignment": None
        }
    ]
    
    for resp in demo_responders:
        db.add_responder(
            responder_id=resp["responder_id"],
            r_type=resp["type"],
            location_text=resp["location_text"],
            latitude=resp["latitude"],
            longitude=resp["longitude"],
            capacity=resp["capacity"],
            availability=resp["availability"],
            status=resp["status"],
            current_assignment=resp["current_assignment"]
        )
