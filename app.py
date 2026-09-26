"""
app.py
Intelligent Emergency Dispatch System -- Streamlit Main Application
B.Tech Academic/Research Prototype featuring HDC, CSP, A* 10x10 Grid Pathfinder, Dynamic Re-planning, SQLite persistence, and Google Maps Navigation Handoff.
Professional enterprise theme (no emojis).
"""

import os
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np

# Import system modules
from environment import THEME_COLORS, DISCLAIMERS, HDC_DIMENSION, GRID_WIDTH, GRID_HEIGHT
import database as db
import demo_data
from incident_detector import detect_incident_type, estimate_severity
import coordinator as coord
from astar_router import render_research_grid, DEMO_GRID_LOCATIONS, DEFAULT_OBSTACLES
import replanner
import dashboard
import navigation

# Streamlit Page Configuration
st.set_page_config(
    page_title="Intelligent Emergency Dispatch System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme & Top Navigation Button Injection
st.markdown(f"""
<style>
    .stApp {{
        background-color: {THEME_COLORS["background"]};
        color: {THEME_COLORS["text"]};
        font-family: 'Inter', -apple-system, sans-serif;
    }}
    .main-header {{
        background-color: {THEME_COLORS["dark_blue"]};
        color: white;
        padding: 22px 30px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.06);
    }}
    .card-panel {{
        background-color: {THEME_COLORS["light_blue"]};
        border: 1px solid {THEME_COLORS["border"]};
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }}
    .badge-success {{
        background-color: {THEME_COLORS["success_green"]};
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
    }}
    .badge-danger {{
        background-color: {THEME_COLORS["emergency_red"]};
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
    }}
    .badge-warning {{
        background-color: {THEME_COLORS["warning_amber"]};
        color: white;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
    }}
    /* Large Prominent Top Navigation Buttons Styling */
    div.stButton > button {{
        height: 52px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        border-radius: 6px !important;
        transition: all 0.2s ease-in-out;
    }}
    div.stButton > button[kind="secondary"] {{
        background-color: #EAF3F8 !important;
        color: #24485C !important;
        border: 1px solid #D5E3EB !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        background-color: #4F8FB3 !important;
        color: #FFFFFF !important;
        border-color: #4F8FB3 !important;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: #2F6F95 !important;
        color: #FFFFFF !important;
        border: 1px solid #24485C !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.12) !important;
    }}
    /* Streamlit metric card dark blue contrast fix */
    [data-testid="stMetricValue"] {{
        color: #24485C !important;
        font-weight: bold !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: #2F6F95 !important;
        font-weight: 600 !important;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize Persistent Database with Demo Data on startup
demo_data.seed_demo_data_if_empty()

# Session State Initialization
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Messages"
if "current_incident_index" not in st.session_state:
    st.session_state.current_incident_index = 0
if "blocked_cells" not in st.session_state:
    st.session_state.blocked_cells = list(DEFAULT_OBSTACLES)

# Enterprise App Header
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size: 26px; color:white; font-weight:800; letter-spacing:0.5px;">INTELLIGENT EMERGENCY DISPATCH SYSTEM</h1>
    <p style="margin:6px 0 0 0; opacity: 0.95; font-size: 14px; color:#EAF3F8;">
        B.Tech Academic Research Prototype | HDC Candidate Screening + CSP Constraints + A* 10x10 Grid Pathfinder
    </p>
</div>
""", unsafe_allow_html=True)

# PROMINENT TOP NAVIGATION BAR (5 Columns with Large Buttons, No Emojis, No Radio Dots)
tcol1, tcol2, tcol3, tcol4, tcol5 = st.columns(5)

with tcol1:
    if st.button("MESSAGES", use_container_width=True, type="primary" if st.session_state.active_tab == "Messages" else "secondary"):
        st.session_state.active_tab = "Messages"
        st.rerun()

with tcol2:
    if st.button("PROCESSING", use_container_width=True, type="primary" if st.session_state.active_tab == "Processing" else "secondary"):
        st.session_state.active_tab = "Processing"
        st.rerun()

with tcol3:
    if st.button("DASHBOARD", use_container_width=True, type="primary" if st.session_state.active_tab == "Dashboard" else "secondary"):
        st.session_state.active_tab = "Dashboard"
        st.rerun()

with tcol4:
    if st.button("NAVIGATION", use_container_width=True, type="primary" if st.session_state.active_tab == "Navigation" else "secondary"):
        st.session_state.active_tab = "Navigation"
        st.rerun()

with tcol5:
    if st.button("SYSTEM INFO", use_container_width=True, type="primary" if st.session_state.active_tab == "More" else "secondary"):
        st.session_state.active_tab = "More"
        st.rerun()

st.markdown("<hr style='margin: 16px 0 24px 0; border: 0; border-top: 1px solid #D5E3EB;'>", unsafe_allow_html=True)

nav_page = st.session_state.active_tab

# Sidebar for System Database Status & Control
st.sidebar.markdown("<h3 style='color:#24485C;'>SQLite System Status</h3>", unsafe_allow_html=True)
db_counts = db.get_table_counts()
st.sidebar.caption(f"Database File: `emergency_dispatch.db`")
st.sidebar.caption(f"Incidents: {db_counts['incidents']} | Messages: {db_counts['messages']}")
st.sidebar.caption(f"Responders: {db_counts['responders']} | Dispatches: {db_counts['dispatches']}")
st.sidebar.markdown("---")

if st.sidebar.button("Reset Demo Database", use_container_width=True):
    db.reset_database()
    demo_data.seed_demo_data_if_empty()
    st.session_state.current_incident_index = 0
    st.session_state.blocked_cells = list(DEFAULT_OBSTACLES)
    st.rerun()

# ==============================================================================
# SCREEN 1: MESSAGES (Default Screen)
# ==============================================================================
if nav_page == "Messages":
    st.markdown("<h2 style='color:#24485C;'>Received Emergency Messages</h2>", unsafe_allow_html=True)
    st.caption("No authentication required. System receives real-time emergency reports into SQLite.")
    
    col_msg_list, col_send = st.columns([1.2, 0.8])
    
    with col_msg_list:
        st.markdown("### Messages Inbox")
        messages = db.get_connection().cursor().execute(
            "SELECT m.*, i.incident_type, i.location_text, i.severity FROM messages m LEFT JOIN incidents i ON m.incident_id = i.incident_id ORDER BY m.timestamp DESC"
        ).fetchall()
        
        for msg in messages:
            st.markdown(f"""
            <div class="card-panel">
                <div style="display:flex; justify-content:space-between;">
                    <strong style="color:#2F6F95; font-size:16px;">Message ID: {msg['message_id']}</strong>
                    <span class="badge-danger">{msg['incident_type'] or 'EMERGENCY'} (Sev {msg['severity'] or 3})</span>
                </div>
                <p style="margin:10px 0; font-weight:500; color:#263842;">"{msg['message_text']}"</p>
                <div style="font-size:12px; color:#64748B;">
                    <span>Location: {msg['location_text'] or 'Shirpur'}</span> | 
                    <span>Time: {msg['timestamp']}</span> | 
                    <span>Source: {msg['source']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_send:
        st.markdown("### Report New Emergency")
        with st.form("new_message_form"):
            new_text = st.text_area("Emergency Message Text", value="Fire emergency reported at Shirpur Market Plaza.")
            new_location = st.text_input("Incident Location Text", value="Shirpur Market Plaza")
            manual_type = st.selectbox("Detected Incident Type", ["Auto Detect", "FIRE", "ACCIDENT", "MEDICAL", "STRUCTURAL"])
            manual_severity = st.slider("Severity Level (1-5)", 1, 5, 4)
            
            submit_btn = st.form_submit_button("Submit Emergency Message", use_container_width=True)
            
            if submit_btn and new_text:
                inc_type = manual_type if manual_type != "Auto Detect" else detect_incident_type(new_text)
                inc_id = f"INC-00{len(db.get_incidents()) + 1}"
                msg_id = f"MSG-{inc_id}"
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                db.create_incident(
                    incident_id=inc_id,
                    incident_type=inc_type,
                    original_message=new_text,
                    location_text=new_location,
                    latitude=21.3540,
                    longitude=74.8830,
                    severity=manual_severity,
                    timestamp=now_str,
                    status="PENDING",
                    source="MANUAL USER REPORT"
                )
                
                db.add_message(
                    message_id=msg_id,
                    incident_id=inc_id,
                    message_text=new_text,
                    timestamp=now_str,
                    source="MANUAL USER REPORT"
                )
                
                # Assign default grid location
                DEMO_GRID_LOCATIONS[inc_id] = (np.random.randint(2, 8), np.random.randint(2, 8))
                st.success(f"Emergency Message {msg_id} submitted! Created Incident {inc_id}.")
                st.rerun()

# ==============================================================================
# SCREEN 2: PROCESSING & EXPLAINABLE DISPATCH
# ==============================================================================
elif nav_page == "Processing":
    st.markdown("<h2 style='color:#24485C;'>Emergency Processing & Decision Engine</h2>", unsafe_allow_html=True)
    
    # Priority Queue Workflow
    pending_queue = coord.get_prioritized_incident_queue()
    
    if not pending_queue:
        st.warning("No incidents found in system database.")
        st.stop()
        
    # Queue Header and Next Emergency Button
    col_q1, col_q2 = st.columns([2, 1])
    with col_q1:
        st.markdown("### Emergency Priority Queue")
        q_summary = " -> ".join([f"#{i['priority_rank']} {i['incident_id']} ({i['incident_type']} Sev {i['severity']})" for i in pending_queue])
        st.info(f"**Queue Order:** {q_summary}")
        
    with col_q2:
        if st.button("NEXT EMERGENCY ->", use_container_width=True, type="primary"):
            st.session_state.current_incident_index = (st.session_state.current_incident_index + 1) % len(pending_queue)
            st.rerun()
            
    # Active Selected Incident
    current_idx = min(st.session_state.current_incident_index, len(pending_queue) - 1)
    active_incident = pending_queue[current_idx]
    active_inc_id = active_incident["incident_id"]
    
    # Run full pipeline for active incident
    pipeline_res = coord.process_single_incident(active_inc_id, force_obstacles=st.session_state.blocked_cells)
    
    st.markdown("---")
    st.markdown(f"## Active Processing Incident: **{active_inc_id}** ({active_incident['incident_type']})")
    
    # Section A: Incident Priority
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("### SECTION A: INCIDENT PRIORITY")
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    col_a1.metric("Priority Rank", f"Rank #{active_incident['priority_rank']}")
    col_a2.metric("Incident Type", active_incident['incident_type'])
    col_a3.metric("Severity Level", f"{active_incident['severity']} / 5")
    col_a4.metric("Urgency Score", active_incident['urgency_score'])
    st.caption(f"Location: `{active_incident['location_text']}` | Original Message: \"{active_incident['original_message']}\"")
    st.caption(f"Academic Note: {DISCLAIMERS['urgency_formula']}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section B: HDC Screening
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("### SECTION B: HDC CANDIDATE SCREENING")
    st.write(f"Evaluating candidate responders in **D = {HDC_DIMENSION:,}** bipolar vector space using runtime NumPy cosine similarity.")
    
    df_hdc = pd.DataFrame(pipeline_res["hdc_results"])
    df_hdc["Shortlisted"] = df_hdc["shortlisted"].apply(lambda x: "YES" if x else "NO")
    df_hdc_display = df_hdc[["responder_id", "type", "capacity", "availability", "hdc_similarity", "Shortlisted"]]
    st.dataframe(df_hdc_display, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section C: CSP Constraint Validation
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("### SECTION C: CSP CONSTRAINT VALIDATION")
    st.write("Enforcing hard domain constraints on HDC-shortlisted candidates (Type Match, Capacity >= Severity, Availability).")
    
    df_csp = pd.DataFrame(pipeline_res["csp_results"])
    df_csp["Result"] = df_csp["csp_valid"].apply(lambda x: "PASS" if x else "FAIL")
    df_csp_display = df_csp[["responder_id", "type", "availability", "capacity", "Result", "rejection_reason"]]
    st.dataframe(df_csp_display, use_container_width=True)
    st.caption(f"Academic Note: {DISCLAIMERS['capacity_rule']}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section D: A* Route Planning & 10x10 Research Grid
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("### SECTION D: A* ROUTE PLANNING & 10x10 RESEARCH GRID")
    
    col_grid, col_routes = st.columns([1.2, 0.8])
    
    with col_grid:
        selected_id = pipeline_res["selected_responder"]["responder_id"] if pipeline_res["selected_responder"] else None
        fig_grid = render_research_grid(
            incident_id=active_inc_id,
            incident_pos=pipeline_res["incident_pos"],
            responders_info=pipeline_res["csp_results"],
            selected_resp_id=selected_id,
            obstacles=pipeline_res["obstacles"]
        )
        st.pyplot(fig_grid)
        
    with col_routes:
        st.markdown("#### Route Evaluation Summary")
        if pipeline_res["routing_evaluations"]:
            df_routes = pd.DataFrame(pipeline_res["routing_evaluations"])
            df_routes_display = df_routes[["responder_id", "type", "distance", "route_cost", "eta_mins"]]
            st.dataframe(df_routes_display, use_container_width=True)
        else:
            st.warning("No CSP valid responders available for route evaluation.")
            
        st.markdown("#### Research Grid Obstacle Controls")
        if st.checkbox("Simulate Blocked Grid Cells"):
            st.info("Click below to toggle obstacle at cell (8, 7) or clear blockages:")
            if st.button("Block Cell (8, 7)"):
                if (8, 7) not in st.session_state.blocked_cells:
                    st.session_state.blocked_cells.append((8, 7))
                    st.rerun()
            if st.button("Clear Blocked Cells"):
                st.session_state.blocked_cells = list(DEFAULT_OBSTACLES)
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section E: Final Decision & Viva Explainability
    st.markdown("<div class='card-panel'>", unsafe_allow_html=True)
    st.markdown("### SECTION E: FINAL DISPATCH DECISION & EXPLAINABILITY")
    
    if pipeline_res["selected_responder"]:
        sel_resp = pipeline_res["selected_responder"]
        disp_rec = pipeline_res["dispatch_record"]
        
        st.markdown(f"""
        <div style="background-color:#EAF3F8; border-left: 6px solid #4FAF7B; padding: 15px; border-radius: 4px;">
            <h3 style="color:#24485C; margin-top:0;">DISPATCH SUCCESSFUL: {sel_resp['responder_id']} ({sel_resp['type']})</h3>
            <p><strong>Route Cost:</strong> {disp_rec['route_cost']:.1f} | <strong>Grid Distance:</strong> {disp_rec['distance']} cells | <strong>Est. ETA:</strong> {disp_rec['eta']} mins</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color:#FDF2F2; border-left: 6px solid #D95C5C; padding: 15px; border-radius: 4px;">
            <h3 style="color:#D95C5C; margin-top:0;">NO RESPONDER ASSIGNED</h3>
            <p>Reason: No HDC-shortlisted candidate passed hard CSP constraints.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("#### Viva Explainability Summary")
    st.text_area(
        "Plain-Language Explanation Log",
        value=pipeline_res["explanations"]["final"] + "\n\n" + pipeline_res["explanations"]["hdc"] + "\n\n" + pipeline_res["explanations"]["csp"] + "\n\n" + pipeline_res["explanations"]["astar"],
        height=220
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Dynamic Re-planning Section
    st.markdown("---")
    st.markdown("### Dynamic Re-planning Simulator")
    st.caption("Test system adaptability when a responder fails or route is blocked.")
    
    col_re1, col_re2 = st.columns(2)
    with col_re1:
        trigger = st.selectbox("Select Trigger Event:", ["RESPONDER_UNAVAILABLE", "ROUTE_BLOCKED", "LOCATION_CHANGED"])
    with col_re2:
        if st.button("Trigger Dynamic Re-planning", use_container_width=True):
            res_repl = replanner.execute_dynamic_replanning(active_inc_id, trigger, st.session_state.blocked_cells)
            st.success(f"Dynamic re-planning complete! Record saved to SQLite route_updates (ID: {res_repl['update_id']}).")
            st.json(res_repl)

# ==============================================================================
# SCREEN 3: DASHBOARD
# ==============================================================================
elif nav_page == "Dashboard":
    dashboard.render_dashboard_view()

# ==============================================================================
# SCREEN 4: NAVIGATION
# ==============================================================================
elif nav_page == "Navigation":
    navigation.render_navigation_view()

# ==============================================================================
# SCREEN 5: MORE / SYSTEM INFORMATION
# ==============================================================================
elif nav_page == "More":
    st.markdown("<h2 style='color:#24485C;'>Research System Configuration & Database</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Research Configuration", "Database Inspector", "About / Contact"])
    
    with sub_tab1:
        st.markdown("### System Architecture & Parameters")
        st.markdown(f"""
        - **HDC Vector Space Dimension ($D$):** `{HDC_DIMENSION:,}` (NumPy Bipolar Vectors {{-1, +1}})
        - **HDC Similarity Metric:** Dynamic Cosine Similarity
        - **Research Grid Size:** `{GRID_WIDTH} x {GRID_HEIGHT}` square grid
        - **A* Movement:** 4-Directional (Up, Down, Left, Right)
        - **A* Heuristic:** Manhattan Distance h(x,y) = |x1-x2| + |y1-y2|
        - **Database:** SQLite3 (`emergency_dispatch.db`) with 6 core tables
        - **Navigation Handoff:** External Google Maps link using physical address strings
        """)
        
    with sub_tab2:
        dashboard.render_database_inspector()
        
    with sub_tab3:
        st.markdown("### Intelligent Emergency Dispatch System")
        st.markdown("""
        **B.Tech Computer Engineering Final Year Project Prototype**
        
        Demonstrating:
        - Hyperdimensional Computing (HDC) Candidate Screening
        - Constraint Satisfaction Problem (CSP) Constraint Validation
        - A* Route Planning on 10x10 Grid
        - Dynamic Re-planning & Rerouting
        - Explainable Artificial Intelligence (XAI)
        - SQLite Database Persistence
        """)
