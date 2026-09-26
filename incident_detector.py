"""
incident_detector.py
Extracts incident features from natural language messages and ranks emergency priority queue.
Calculates Urgency Score: Urgency = Severity * 10 + Waiting Time (minutes).
"""

import re
from datetime import datetime
from environment import DISCLAIMERS

INCIDENT_TYPES = ["FIRE", "ACCIDENT", "MEDICAL", "STRUCTURAL"]

def detect_incident_type(message_text):
    """Normalized keyword matching to extract incident type."""
    text_lower = message_text.lower()
    
    if any(k in text_lower for k in ["fire", "flame", "smoke", "blaze", "burn"]):
        return "FIRE"
    elif any(k in text_lower for k in ["accident", "crash", "collision", "hit", "wreck"]):
        return "ACCIDENT"
    elif any(k in text_lower for k in ["medical", "cardiac", "patient", "injury", "bleeding", "ambulance", "hospital"]):
        return "MEDICAL"
    elif any(k in text_lower for k in ["structural", "building collapse", "wall", "roof"]):
        return "STRUCTURAL"
    return "ACCIDENT"  # Default fallback

def estimate_severity(message_text, incident_type):
    """Rules-based severity estimation (Range 1 to 5)."""
    text_lower = message_text.lower()
    
    if any(k in text_lower for k in ["critical", "severe", "massive", "multiple", "trapped"]):
        return 5
    elif any(k in text_lower for k in ["major", "urgent", "heavy"]):
        return 4
    elif any(k in text_lower for k in ["moderate", "medium"]):
        return 3
    else:
        # Default type-based severity baselines
        baselines = {"FIRE": 5, "ACCIDENT": 3, "MEDICAL": 2, "STRUCTURAL": 4}
        return baselines.get(incident_type, 3)

def calculate_waiting_time_minutes(timestamp_str):
    """Calculates waiting time in minutes from ISO/formatted timestamp."""
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - ts
        minutes = max(0, int(delta.total_seconds() / 60))
        return minutes
    except Exception:
        return 0

def calculate_urgency_score(severity, waiting_time_minutes):
    """
    Urgency Score Formula:
    Urgency = Severity * 10 + Waiting Time
    (Academic simulation rule for queue ordering).
    """
    return (severity * 10) + waiting_time_minutes

def rank_emergency_queue(incidents_list):
    """
    Ranks pending emergency incidents by urgency score descending.
    Returns list of dicts with calculated urgency details.
    """
    ranked = []
    for inc in incidents_list:
        wait_min = calculate_waiting_time_minutes(inc["timestamp"])
        urgency = calculate_urgency_score(inc["severity"], wait_min)
        
        inc_copy = dict(inc)
        inc_copy["waiting_time_min"] = wait_min
        inc_copy["urgency_score"] = urgency
        ranked.append(inc_copy)
        
    # Sort primarily by urgency score descending, secondarily by timestamp ascending
    ranked.sort(key=lambda x: (x["urgency_score"], -x["severity"]), reverse=True)
    
    # Assign queue ranks
    for rank_idx, item in enumerate(ranked, start=1):
        item["priority_rank"] = rank_idx
        
    return ranked
