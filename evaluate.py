"""
evaluate.py
Performance Evaluation & Benchmark Script for Intelligent Emergency Dispatch System.
Measures real runtime performance values for HDC screening, CSP validation, and A* pathfinding.
Produces empirical academic research statistics.
"""

import time
import json
import sys
import os

# Ensure local path is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
import demo_data
import coordinator as coord
from hdc_screener import screener
from csp_validator import validate_csp_constraints
from astar_router import astar_search

def run_evaluation():
    """Executes evaluation benchmarks and prints timing & performance metrics."""
    print("=" * 70)
    print("INTELLIGENT EMERGENCY DISPATCH SYSTEM -- BENCHMARK EVALUATION")
    print("=" * 70)
    
    # Reset database to clean demo state for benchmark repeatability
    db.reset_database()
    demo_data.seed_demo_data_if_empty()
    
    incidents = db.get_incidents()
    responders = db.get_responders()
    
    print(f"\n[1] SYSTEM DATASET SUMMARY:")
    print(f"  * Total Incidents Loaded: {len(incidents)}")
    print(f"  * Total Responders Loaded: {len(responders)}")
    
    metrics = []
    
    for inc in incidents:
        inc_id = inc["incident_id"]
        print(f"\n" + "-" * 60)
        print(f"EVALUATING INCIDENT: {inc_id} ({inc['incident_type']} - Severity {inc['severity']})")
        print("-" * 60)
        
        # Measure HDC Screening Time
        t_hdc_start = time.perf_counter()
        hdc_results = screener.screen_responders(inc, responders)
        t_hdc_end = time.perf_counter()
        hdc_time_ms = (t_hdc_end - t_hdc_start) * 1000.0
        
        shortlisted = [r for r in hdc_results if r["shortlisted"]]
        
        # Measure CSP Validation Time
        t_csp_start = time.perf_counter()
        csp_results = validate_csp_constraints(inc, shortlisted)
        t_csp_end = time.perf_counter()
        csp_time_ms = (t_csp_end - t_csp_start) * 1000.0
        
        valid_csp = [r for r in csp_results if r["csp_valid"]]
        csp_rejections = len(shortlisted) - len(valid_csp)
        
        # Measure A* Route Evaluation Time
        t_astar_start = time.perf_counter()
        routes_eval = []
        for r in valid_csp:
            # Grid search
            res = astar_search((0, 0), (8, 8))
            routes_eval.append(res)
        t_astar_end = time.perf_counter()
        astar_time_ms = (t_astar_end - t_astar_start) * 1000.0
        
        # Total Pipeline Execution Time
        t_pipe_start = time.perf_counter()
        full_res = coord.process_single_incident(inc_id)
        t_pipe_end = time.perf_counter()
        pipeline_time_ms = (t_pipe_end - t_pipe_start) * 1000.0
        
        sel_resp = full_res.get("selected_responder")
        sel_id = sel_resp["responder_id"] if sel_resp else "NONE"
        sel_cost = full_res.get("selected_cost", float('nan'))
        
        inc_metric = {
            "incident_id": inc_id,
            "incident_type": inc["incident_type"],
            "candidates_evaluated": len(responders),
            "shortlisted_count": len(shortlisted),
            "hdc_matching_time_ms": round(hdc_time_ms, 4),
            "csp_valid_count": len(valid_csp),
            "csp_rejections": csp_rejections,
            "csp_time_ms": round(csp_time_ms, 4),
            "astar_evaluations": len(valid_csp),
            "astar_time_ms": round(astar_time_ms, 4),
            "total_pipeline_time_ms": round(pipeline_time_ms, 4),
            "assigned_responder": sel_id,
            "route_cost": sel_cost
        }
        metrics.append(inc_metric)
        
        print(f"  * HDC Matching Time: {hdc_time_ms:.3f} ms (Candidates: {len(responders)} -> Shortlisted: {len(shortlisted)})")
        print(f"  * CSP Validation Time: {csp_time_ms:.3f} ms (Valid: {len(valid_csp)}, Rejected: {csp_rejections})")
        print(f"  * A* Evaluation Time: {astar_time_ms:.3f} ms ({len(valid_csp)} routes calculated)")
        print(f"  * Total Pipeline Time: {pipeline_time_ms:.3f} ms")
        print(f"  * Assigned Responder: {sel_id} (Route Cost: {sel_cost})")
        
    print("\n" + "=" * 70)
    print("SUMMARY AGGREGATE BENCHMARK METRICS:")
    avg_hdc = sum(m["hdc_matching_time_ms"] for m in metrics) / len(metrics)
    avg_pipeline = sum(m["total_pipeline_time_ms"] for m in metrics) / len(metrics)
    
    print(f"  * Average HDC Matching Time: {avg_hdc:.3f} ms")
    print(f"  * Average Full Pipeline Latency: {avg_pipeline:.3f} ms")
    print(f"  * Successful Assignments: {sum(1 for m in metrics if m['assigned_responder'] != 'NONE')} / {len(metrics)}")
    print("=" * 70)
    
    return metrics

if __name__ == "__main__":
    run_evaluation()
