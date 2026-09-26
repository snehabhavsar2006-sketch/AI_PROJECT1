"""
test_system.py
Automated Unit and System Test Suite for Intelligent Emergency Dispatch System.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "emergency_dispatch_system"))

import database as db
import demo_data
from incident_detector import detect_incident_type, estimate_severity, rank_emergency_queue
from hdc_screener import screener
from csp_validator import validate_csp_constraints
from astar_router import astar_search, manhattan_distance
import coordinator as coord
import replanner
from navigation import build_google_maps_url

def test_all():
    print("RUNNING SYSTEM UNIT TESTS...")
    
    # Test 1: Database Initialization & Seeding
    db.reset_database()
    demo_data.seed_demo_data_if_empty()
    counts = db.get_table_counts()
    assert counts["incidents"] >= 3, "Failed: Database incidents count < 3"
    assert counts["responders"] >= 5, "Failed: Database responders count < 5"
    print("[PASS] Test 1 Passed: Database schema & demo seeding verified.")
    
    # Test 2: Incident Detection & Priority Ranking
    inc_type = detect_incident_type("Fire reported near NMIMS Shirpur campus")
    assert inc_type == "FIRE", f"Failed: Expected FIRE, got {inc_type}"
    
    incidents = db.get_incidents()
    ranked = rank_emergency_queue(incidents)
    assert len(ranked) == 3, "Failed: Priority queue length mismatch"
    assert ranked[0]["incident_id"] == "INC-001", "Failed: INC-001 should be Rank 1"
    print("[PASS] Test 2 Passed: Incident detection & urgency priority queue verified.")
    
    # Test 3: HDC Vector Symbolic Architecture Screening
    inc = db.get_incident("INC-001")
    responders = db.get_responders()
    hdc_res = screener.screen_responders(inc, responders)
    assert len(hdc_res) == len(responders), "Failed: HDC evaluation count mismatch"
    assert all("hdc_similarity" in r for r in hdc_res), "Failed: HDC similarity missing"
    print("[PASS] Test 3 Passed: HDC vector similarity screening verified.")
    
    # Test 4: CSP Validation Rules
    shortlisted = [r for r in hdc_res if r["shortlisted"]]
    csp_res = validate_csp_constraints(inc, shortlisted)
    resp2_csp = next(r for r in csp_res if r["responder_id"] == "RESP-002")
    assert resp2_csp["csp_valid"] == True, "Failed: RESP-002 should pass CSP for FIRE"
    resp1_csp = next(r for r in csp_res if r["responder_id"] == "RESP-001")
    assert resp1_csp["csp_valid"] == False, "Failed: RESP-001 (ambulance) should fail CSP for FIRE"
    print("[PASS] Test 4 Passed: CSP hard constraint validation verified.")
    
    # Test 5: A* Grid Pathfinding
    a_res = astar_search((0, 1), (8, 8))
    assert a_res["success"] == True, "Failed: A* path search failed"
    assert a_res["route_cost"] > 0, "Failed: Invalid route cost"
    assert manhattan_distance((0, 1), (8, 8)) == 15, "Failed: Manhattan distance calculation"
    print("[PASS] Test 5 Passed: A* 10x10 research grid pathfinding verified.")
    
    # Test 6: Full Dispatch Pipeline & Database Persistence
    disp_res = coord.process_single_incident("INC-001")
    assert disp_res["selected_responder"]["responder_id"] == "RESP-002", "Failed: RESP-002 not selected for INC-001"
    history = db.get_dispatch_history()
    assert len(history) >= 1, "Failed: Dispatch history record missing"
    print("[PASS] Test 6 Passed: Master dispatch pipeline & SQLite persistence verified.")
    
    # Test 7: Dynamic Re-planning Engine
    re_res = replanner.execute_dynamic_replanning("INC-001", "RESPONDER_UNAVAILABLE")
    assert re_res["success"] == True, "Failed: Dynamic re-planning execution failed"
    updates = db.get_connection().cursor().execute("SELECT COUNT(*) FROM route_updates").fetchone()[0]
    assert updates >= 1, "Failed: Route updates record missing in database"
    print("[PASS] Test 7 Passed: Dynamic re-planning & failover logging verified.")
    
    # Test 8: Navigation Handoff URL Construction
    url = build_google_maps_url("Shirpur Station Road", "NMIMS Shirpur")
    assert "google.com/maps/dir" in url, "Failed: Invalid Google Maps URL format"
    assert "Shirpur+Station+Road" in url or "Shirpur" in url, "Failed: Address missing in URL"
    print("[PASS] Test 8 Passed: External Google Maps handoff URL builder verified.")
    
    print("\nALL 8 SYSTEM UNIT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all()
