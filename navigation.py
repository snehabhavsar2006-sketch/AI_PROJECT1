"""
navigation.py
Driver Location & Real-World Navigation Handoff Component.
Generates dynamic Google Maps navigation URLs using stored physical addresses.
Maintains explicit distinction between 10x10 A* research grid and external Google Maps navigation.
Professional enterprise theme (no emojis).
"""

import urllib.parse
import streamlit as st
import database as db
from environment import THEME_COLORS, DISCLAIMERS

def build_google_maps_url(origin_address, destination_address):
    """
    Constructs an external Google Maps Directions URL.
    Origin = Stored responder address from SQLite.
    Destination = Extracted incident location from emergency message.
    """
    base_url = "https://www.google.com/maps/dir/?api=1"
    params = {
        "origin": origin_address,
        "destination": destination_address,
        "travelmode": "driving"
    }
    encoded = urllib.parse.urlencode(params)
    return f"{base_url}&{encoded}"

def render_navigation_view(selected_incident_id=None, selected_responder_id=None):
    """Renders the Driver Location & Navigation handoff view."""
    st.markdown("<h2 style='color:#24485C;'>Driver Location & Navigation Handoff</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.info(f"Academic Distinction Note: {DISCLAIMERS['google_maps_handoff']}")
    
    # Fetch active dispatch or allow selection from DB history
    dispatches = db.get_dispatch_history()
    
    if not dispatches:
        st.warning("No active dispatches available for navigation. Please process an emergency first.")
        return
        
    # Select active dispatch
    dispatch_options = {f"{d['dispatch_id']} -- {d['incident_id']} ({d['incident_type']}) -> {d['responder_id']}": d for d in dispatches}
    selected_key = st.selectbox("Select Active Dispatch Record:", list(dispatch_options.keys()))
    dispatch = dispatch_options[selected_key]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div style='background-color:#EAF3F8; padding: 18px; border-radius: 6px; border: 1px solid #D5E3EB;'>", unsafe_allow_html=True)
        st.markdown("### Selected Responder")
        st.write(f"**Responder ID:** `{dispatch['responder_id']}`")
        st.write(f"**Vehicle Type:** `{dispatch['responder_type']}`")
        st.write(f"**Depot / Stored Address:** `{dispatch['responder_location']}`")
        st.caption(f"Location Source: {DISCLAIMERS['location_source']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div style='background-color:#EAF3F8; padding: 18px; border-radius: 6px; border: 1px solid #D5E3EB;'>", unsafe_allow_html=True)
        st.markdown("### Emergency Target Location")
        st.write(f"**Incident ID:** `{dispatch['incident_id']}`")
        st.write(f"**Incident Type:** `{dispatch['incident_type']}`")
        st.write(f"**Target Address:** `{dispatch['incident_location']}`")
        st.caption("Extracted from emergency message.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate Google Maps Handoff URL
    origin_addr = dispatch['responder_location']
    dest_addr = dispatch['incident_location']
    maps_url = build_google_maps_url(origin_addr, dest_addr)
    
    st.markdown("<div style='background-color:#F5F9FC; border: 2px dashed #4F8FB3; padding: 24px; text-align: center; border-radius: 8px;'>", unsafe_allow_html=True)
    st.markdown("### Real-World Navigation Handoff Link")
    st.write(f"**Origin (Database Address):** {origin_addr}")
    st.write(f"**Destination (Message Location):** {dest_addr}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(
        f'<a href="{maps_url}" target="_blank" style="background-color:#2F6F95; color:white; padding:14px 28px; text-decoration:none; border-radius:6px; font-weight:bold; font-size:16px; letter-spacing:0.5px;">OPEN NAVIGATION IN GOOGLE MAPS</a>',
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
