"""
environment.py
System-wide configuration, styling tokens, algorithm hyperparameters, and academic disclaimers.
Intelligent Emergency Dispatch System (B.Tech Research Prototype)
"""

import os

# Base Directory & Database Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "emergency_dispatch.db"
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

# UI Theme & Color Palette (Section 25 Specification)
THEME_COLORS = {
    "background": "#F5F9FC",      # Clean light canvas
    "primary_blue": "#2F6F95",    # Main brand blue
    "dark_blue": "#24485C",       # Accent dark blue for headings
    "light_blue": "#EAF3F8",      # Section container background
    "border": "#D5E3EB",          # Subtle divider border
    "active_blue": "#4F8FB3",     # Interactive active tab / highlight
    "success_green": "#4FAF7B",   # Valid state / assigned badge
    "warning_amber": "#E3A44A",   # Rejected / warning alert
    "emergency_red": "#D95C5C",   # Emergency / critical alert
    "text": "#263842",            # High-contrast readable typography
}

# HDC Hyperparameters (Section 14 Specification)
HDC_DIMENSION = 10000  # D = 10,000 hypervector dimensionality
HDC_SHORTLIST_THRESHOLD = 0.15  # Cosine similarity cut-off for shortlist

# A* Research Grid Hyperparameters (Section 16 & 17 Specification)
GRID_WIDTH = 10
GRID_HEIGHT = 10
GRID_MOVEMENT = 4  # 4-directional: Up, Down, Left, Right
DEFAULT_OBSTACLES = [(3, 3), (3, 4), (3, 5), (6, 2), (6, 3), (7, 6), (7, 7)]

# Vehicle Types and Compatibility mapping for CSP
COMPATIBILITY_RULES = {
    "FIRE": ["fire_truck", "rescue_unit"],
    "ACCIDENT": ["ambulance", "rescue_unit", "police", "fire_truck"],
    "MEDICAL": ["ambulance"],
    "STRUCTURAL": ["fire_truck", "rescue_unit"]
}

# Academic Disclaimers (Section 13, 15, 24, 31, 41)
DISCLAIMERS = {
    "urgency_formula": "This urgency formula (Urgency = Severity × 10 + Waiting Time) is a simplified simulation rule used only to establish processing order in this academic prototype.",
    "capacity_rule": "The capacity rule (Responder Capacity ≥ Incident Severity) is a simplified prototype constraint for academic simulation.",
    "google_maps_handoff": "Our A* algorithm is demonstrated on the 10×10 research grid. Google Maps is used strictly for external real-world navigation handoff using physical addresses.",
    "location_source": "DEMO SIMULATION DATA — Coordinates are configured for prototype demonstration."
}
