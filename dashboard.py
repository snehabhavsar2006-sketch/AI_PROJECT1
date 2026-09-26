"""
dashboard.py
Analytical Dashboard Component for Intelligent Emergency Dispatch System.
Renders active dispatch status, explainable decisions, dispatch history, and live SQLite database inspection.
Professional enterprise theme (no emojis).
"""

import streamlit as st
import pandas as pd
import database as db
from environment import THEME_COLORS, DISCLAIMERS

def render_dashboard_view(active_incident_id=None):
    """Renders the main analytics dashboard view with high-contrast UI metrics."""
    st.markdown("<h2 style='color:#24485C;'>Executive Emergency Dashboard</h2>", unsafe_allow_html=True)
    st.caption("Live monitoring of emergency incidents, active responder dispatches, and SQLite database persistence.")
    st.markdown("---")
    
    # System Metrics Overview (High-contrast HTML Cards for crystal clear visibility)
    incidents = db.get_incidents()
    pending = [i for i in incidents if i["status"] == "PENDING"]
    dispatched = [i for i in incidents if i["status"] == "DISPATCHED"]
    table_counts = db.get_table_counts()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background-color:#EAF3F8; border:1px solid #D5E3EB; border-radius:8px; padding:16px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="color:#2F6F95; font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">Total Incidents</div>
            <div style="color:#24485C; font-weight:800; font-size:32px; margin-top:6px;">{len(incidents)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background-color:#EAF3F8; border:1px solid #D5E3EB; border-radius:8px; padding:16px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="color:#2F6F95; font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">Pending Emergencies</div>
            <div style="color:#D95C5C; font-weight:800; font-size:32px; margin-top:6px;">{len(pending)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background-color:#EAF3F8; border:1px solid #D5E3EB; border-radius:8px; padding:16px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="color:#2F6F95; font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">Dispatched Emergencies</div>
            <div style="color:#4FAF7B; font-weight:800; font-size:32px; margin-top:6px;">{len(dispatched)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style="background-color:#EAF3F8; border:1px solid #D5E3EB; border-radius:8px; padding:16px; text-align:center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
            <div style="color:#2F6F95; font-weight:700; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">SQLite DB Records</div>
            <div style="color:#24485C; font-weight:800; font-size:32px; margin-top:6px;">{sum(table_counts.values())}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Active Dispatch Focus Panel
    history = db.get_dispatch_history()
    if history:
        latest = history[0]
        st.markdown(f"""
        <div style="background-color:#EAF3F8; border-left: 6px solid #2F6F95; border-top:1px solid #D5E3EB; border-right:1px solid #D5E3EB; border-bottom:1px solid #D5E3EB; padding: 20px; border-radius: 6px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="color:#24485C; margin:0; font-size:20px; font-weight:700;">Active Dispatch Focus -- {latest['incident_id']}</h3>
                <span style="background-color:#4FAF7B; color:white; padding:4px 12px; border-radius:4px; font-weight:bold; font-size:12px; letter-spacing:0.5px;">STATUS: {latest['status']}</span>
            </div>
            <hr style="border:0; border-top:1px solid #D5E3EB; margin:14px 0;">
            <div style="color:#263842; font-size:15px; line-height:1.6;">
                <p style="margin:4px 0;"><strong>Incident Type:</strong> <span style="color:#D95C5C; font-weight:bold;">{latest['incident_type']}</span> | <strong>Target Location:</strong> {latest['incident_location']}</p>
                <p style="margin:4px 0;"><strong>Assigned Responder:</strong> <span style="color:#2F6F95; font-weight:bold;">{latest['responder_id']} ({latest['responder_type']})</span></p>
                <p style="margin:4px 0;"><strong>Depot / Station Address:</strong> {latest['responder_location']}</p>
                <p style="margin:4px 0;"><strong>Grid Path Cost:</strong> {latest['route_cost']:.1f} | <strong>Grid Distance:</strong> {latest['distance']} cells | <strong>Est. ETA:</strong> {latest['eta']} mins</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No active dispatches recorded yet. Use the 'Processing' menu to assign responders.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dispatch History Log Table from SQLite
    st.markdown("### SQLite Persistent Dispatch Audit Log")
    if history:
        df_hist = pd.DataFrame(history)
        df_display = df_hist[[
            "dispatch_id", "incident_id", "incident_type", "responder_id", 
            "responder_type", "route_cost", "distance", "eta", "assigned_at", "status"
        ]]
        st.dataframe(df_display, use_container_width=True)
    else:
        st.write("No dispatch records found in SQLite database `dispatches` table.")
        
    # Database Table Inspector
    render_database_inspector()

def render_database_inspector():
    """Renders the SQLite Database & System Information tab (Section 30 Specification)."""
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#24485C;'>SQLite Database Inspector</h3>", unsafe_allow_html=True)
    st.caption("Direct read access to physical database `emergency_dispatch.db` tables.")
    
    counts = db.get_table_counts()
    st.write(f"**Database Status:** Connected (`emergency_dispatch.db`) | Total Records: {sum(counts.values())}")
    
    tabs = st.tabs(["Messages", "Incidents", "Responders", "Dispatches", "Processing Results", "Route Updates"])
    
    conn = db.get_connection()
    
    with tabs[0]:
        df = pd.read_sql_query("SELECT * FROM messages", conn)
        st.dataframe(df, use_container_width=True)
        
    with tabs[1]:
        df = pd.read_sql_query("SELECT * FROM incidents", conn)
        st.dataframe(df, use_container_width=True)
        
    with tabs[2]:
        df = pd.read_sql_query("SELECT * FROM responders", conn)
        st.dataframe(df, use_container_width=True)
        
    with tabs[3]:
        df = pd.read_sql_query("SELECT * FROM dispatches", conn)
        st.dataframe(df, use_container_width=True)
        
    with tabs[4]:
        df = pd.read_sql_query("SELECT * FROM processing_results", conn)
        st.dataframe(df, use_container_width=True)
        
    with tabs[5]:
        df = pd.read_sql_query("SELECT * FROM route_updates", conn)
        st.dataframe(df, use_container_width=True)
        
    conn.close()
