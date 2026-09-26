"""
database.py
Pure SQLite3 interface for persistent emergency dispatch system data.
Uses parameterized queries to prevent SQL injection and maintains foreign key constraints.
"""

import sqlite3
import os
from environment import DB_PATH

def get_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initializes the database schema with the 6 required core tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            incident_id TEXT,
            message_text TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT DEFAULT 'DEMO SIMULATION',
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
        )
    """)
    
    # 2. incidents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            incident_type TEXT NOT NULL,
            original_message TEXT NOT NULL,
            location_text TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            severity INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            source TEXT DEFAULT 'DEMO SIMULATION'
        )
    """)
    
    # 3. responders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responders (
            responder_id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            location_text TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            capacity INTEGER NOT NULL,
            availability INTEGER DEFAULT 1,
            status TEXT DEFAULT 'AVAILABLE',
            current_assignment TEXT
        )
    """)
    
    # 4. dispatches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispatches (
            dispatch_id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            responder_id TEXT NOT NULL,
            assigned_at TEXT NOT NULL,
            route TEXT NOT NULL,
            route_cost REAL NOT NULL,
            distance REAL NOT NULL,
            eta REAL NOT NULL,
            status TEXT DEFAULT 'DISPATCHED',
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id),
            FOREIGN KEY (responder_id) REFERENCES responders (responder_id)
        )
    """)
    
    # 5. processing_results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_results (
            processing_id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            responder_id TEXT NOT NULL,
            hdc_similarity REAL NOT NULL,
            shortlisted INTEGER NOT NULL,
            csp_valid INTEGER NOT NULL,
            rejection_reason TEXT,
            route_cost REAL,
            distance REAL,
            eta REAL,
            selected INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id),
            FOREIGN KEY (responder_id) REFERENCES responders (responder_id)
        )
    """)
    
    # 6. route_updates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS route_updates (
            update_id TEXT PRIMARY KEY,
            incident_id TEXT NOT NULL,
            old_route TEXT,
            new_route TEXT NOT NULL,
            reason TEXT NOT NULL,
            old_cost REAL,
            new_cost REAL NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
        )
    """)
    
    conn.commit()
    conn.close()

# CRUD Functions

def add_message(message_id, incident_id, message_text, timestamp, source="DEMO SIMULATION"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (message_id, incident_id, message_text, timestamp, source) VALUES (?, ?, ?, ?, ?)",
        (message_id, incident_id, message_text, timestamp, source)
    )
    conn.commit()
    conn.close()

def create_incident(incident_id, incident_type, original_message, location_text, latitude, longitude, severity, timestamp, status="PENDING", source="DEMO SIMULATION"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO incidents 
           (incident_id, incident_type, original_message, location_text, latitude, longitude, severity, timestamp, status, source) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (incident_id, incident_type, original_message, location_text, latitude, longitude, severity, timestamp, status, source)
    )
    conn.commit()
    conn.close()

def get_incidents(status=None):
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM incidents WHERE status = ? ORDER BY timestamp ASC", (status,))
    else:
        cursor.execute("SELECT * FROM incidents ORDER BY timestamp ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_incident(incident_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidents WHERE incident_id = ?", (incident_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_responder(responder_id, r_type, location_text, latitude, longitude, capacity, availability=1, status="AVAILABLE", current_assignment=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO responders 
           (responder_id, type, location_text, latitude, longitude, capacity, availability, status, current_assignment) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (responder_id, r_type, location_text, latitude, longitude, capacity, availability, status, current_assignment)
    )
    conn.commit()
    conn.close()

def get_responders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responders ORDER BY responder_id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_available_responders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM responders WHERE availability = 1 ORDER BY responder_id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def update_responder_location(responder_id, location_text, latitude, longitude):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE responders SET location_text = ?, latitude = ?, longitude = ? WHERE responder_id = ?",
        (location_text, latitude, longitude, responder_id)
    )
    conn.commit()
    conn.close()

def update_responder_status(responder_id, availability, status, current_assignment=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE responders SET availability = ?, status = ?, current_assignment = ? WHERE responder_id = ?",
        (1 if availability else 0, status, current_assignment, responder_id)
    )
    conn.commit()
    conn.close()

def create_dispatch(dispatch_id, incident_id, responder_id, assigned_at, route, route_cost, distance, eta, status="DISPATCHED"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO dispatches 
           (dispatch_id, incident_id, responder_id, assigned_at, route, route_cost, distance, eta, status) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (dispatch_id, incident_id, responder_id, assigned_at, route, route_cost, distance, eta, status)
    )
    conn.commit()
    conn.close()

def save_processing_result(processing_id, incident_id, responder_id, hdc_similarity, shortlisted, csp_valid, rejection_reason, route_cost, distance, eta, selected, timestamp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO processing_results 
           (processing_id, incident_id, responder_id, hdc_similarity, shortlisted, csp_valid, rejection_reason, route_cost, distance, eta, selected, timestamp) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (processing_id, incident_id, responder_id, hdc_similarity, 1 if shortlisted else 0, 1 if csp_valid else 0, rejection_reason, route_cost, distance, eta, 1 if selected else 0, timestamp)
    )
    conn.commit()
    conn.close()

def save_route_update(update_id, incident_id, old_route, new_route, reason, old_cost, new_cost, timestamp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO route_updates 
           (update_id, incident_id, old_route, new_route, reason, old_cost, new_cost, timestamp) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (update_id, incident_id, old_route, new_route, reason, old_cost, new_cost, timestamp)
    )
    conn.commit()
    conn.close()

def update_incident_status(incident_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE incidents SET status = ? WHERE incident_id = ?", (status, incident_id))
    conn.commit()
    conn.close()

def get_dispatch_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.*, i.incident_type, i.location_text as incident_location, r.type as responder_type, r.location_text as responder_location
        FROM dispatches d
        JOIN incidents i ON d.incident_id = i.incident_id
        JOIN responders r ON d.responder_id = r.responder_id
        ORDER BY d.assigned_at DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_processing_results(incident_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if incident_id:
        cursor.execute("SELECT * FROM processing_results WHERE incident_id = ? ORDER BY hdc_similarity DESC", (incident_id,))
    else:
        cursor.execute("SELECT * FROM processing_results ORDER BY timestamp DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_table_counts():
    conn = get_connection()
    cursor = conn.cursor()
    tables = ["messages", "incidents", "responders", "dispatches", "processing_results", "route_updates"]
    counts = {}
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = cursor.fetchone()[0]
    conn.close()
    return counts

def reset_database():
    """Utility to clear database if clean state is required."""
    conn = get_connection()
    cursor = conn.cursor()
    tables = ["messages", "incidents", "responders", "dispatches", "processing_results", "route_updates"]
    for t in tables:
        cursor.execute(f"DELETE FROM {t}")
    conn.commit()
    conn.close()
