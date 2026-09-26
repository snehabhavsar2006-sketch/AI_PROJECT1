"""
astar_router.py
A* Route Planning algorithm on a 10×10 research grid.
Uses Manhattan distance heuristic h(x,y) = |x1-x2| + |y1-y2| with 4-directional movement.
Renders high-quality research grid visualizations using Matplotlib.
"""

import heapq
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from environment import GRID_WIDTH, GRID_HEIGHT, DEFAULT_OBSTACLES, THEME_COLORS

# Grid coordinate mapping for demo responders and incidents
DEMO_GRID_LOCATIONS = {
    "INC-001": (8, 8),  # NMIMS Shirpur
    "INC-002": (1, 8),  # Shirpur Highway
    "INC-003": (5, 5),  # Shirpur Central Market
    "RESP-001": (0, 1), # Shirpur Station Road (Loc A)
    "RESP-002": (1, 1), # Shirpur Industrial Zone (Loc B)
    "RESP-003": (8, 2), # Shirpur Substation Depot (Loc C)
    "RESP-004": (2, 2), # Shirpur Hospital Bay (Loc D)
    "RESP-005": (5, 0), # Shirpur Police HQ (Loc E)
}

def manhattan_distance(p1, p2):
    """Heuristic function h(n): Manhattan distance between two grid cells."""
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_neighbors(pos, width=GRID_WIDTH, height=GRID_HEIGHT, obstacles=None):
    """Returns valid 4-directional neighbors (Up, Down, Left, Right)."""
    if obstacles is None:
        obstacles = set()
        
    x, y = pos
    candidates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    valid = []
    for cx, cy in candidates:
        if 0 <= cx < width and 0 <= cy < height:
            if (cx, cy) not in obstacles:
                valid.append((cx, cy))
    return valid

def astar_search(start, goal, width=GRID_WIDTH, height=GRID_HEIGHT, obstacles=None):
    """
    Executes A* pathfinding from start cell to goal cell.
    Returns dict containing path (list of coordinates), route_cost, distance, nodes_evaluated.
    """
    if obstacles is None:
        obstacles = set(DEFAULT_OBSTACLES)
    else:
        obstacles = set(obstacles)
        
    # Priority Queue storing tuples: (f_score, g_score, current_pos, path)
    open_set = []
    heapq.heappush(open_set, (manhattan_distance(start, goal), 0, start, [start]))
    
    g_scores = {start: 0}
    nodes_evaluated = 0
    
    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        nodes_evaluated += 1
        
        if current == goal:
            return {
                "success": True,
                "path": path,
                "distance": len(path) - 1,
                "route_cost": float(g),
                "nodes_evaluated": nodes_evaluated
            }
            
        for neighbor in get_neighbors(current, width, height, obstacles):
            # Step cost = 1.0 (can be extended with terrain weights)
            tentative_g = g + 1.0
            
            if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                g_scores[neighbor] = tentative_g
                h = manhattan_distance(neighbor, goal)
                f_neighbor = tentative_g + h
                heapq.heappush(open_set, (f_neighbor, tentative_g, neighbor, path + [neighbor]))
                
    # No path found
    return {
        "success": False,
        "path": [],
        "distance": float('inf'),
        "route_cost": float('inf'),
        "nodes_evaluated": nodes_evaluated
    }

def render_research_grid(incident_id, incident_pos, responders_info, selected_resp_id, obstacles=None):
    """
    Renders a 10×10 Matplotlib visual research grid with clear color coding:
    - Incident: RED marker
    - Selected Responder: DARK BLUE marker
    - Other Responders: LIGHT BLUE marker
    - Selected A* Route: GREEN path
    - Alternative Routes: ORANGE path
    - Blocked Cells: DARK GRAY squares
    """
    if obstacles is None:
        obstacles = DEFAULT_OBSTACLES

    fig, ax = plt.subplots(figsize=(7, 7), dpi=100)
    fig.patch.set_facecolor(THEME_COLORS["background"])
    ax.set_facecolor(THEME_COLORS["light_blue"])
    
    # Draw 10x10 Grid background squares
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = patches.Rectangle((x, y), 1, 1, linewidth=0.5, edgecolor=THEME_COLORS["border"], facecolor="#FFFFFF")
            ax.add_patch(rect)
            
    # Draw Obstacles (Blocked Cells - Dark Gray)
    for (ox, oy) in obstacles:
        rect = patches.Rectangle((ox, oy), 1, 1, linewidth=0.5, edgecolor="#1E293B", facecolor="#475569")
        ax.add_patch(rect)
        ax.text(ox + 0.5, oy + 0.5, "✖", color="#FFFFFF", fontsize=10, ha="center", va="center", fontweight="bold")
        
    # Compute and plot routes for valid responders
    alternative_paths = []
    selected_path = []
    
    for r_info in responders_info:
        r_id = r_info["responder_id"]
        if not r_info.get("csp_valid", False):
            continue
            
        r_pos = DEMO_GRID_LOCATIONS.get(r_id, (0, 0))
        res = astar_search(r_pos, incident_pos, obstacles=obstacles)
        
        if res["success"]:
            if r_id == selected_resp_id:
                selected_path = res["path"]
            else:
                alternative_paths.append((r_id, res["path"]))
                
    # Plot Alternative Candidate Routes (ORANGE dashed lines)
    for r_id, path in alternative_paths:
        px = [p[0] + 0.5 for p in path]
        py = [p[1] + 0.5 for p in path]
        ax.plot(px, py, color="#F97316", linewidth=2.5, linestyle="--", alpha=0.75, label=f"Alt Route ({r_id})", zorder=3)
        
    # Plot Selected Route (GREEN bold line with arrows)
    if selected_path:
        px = [p[0] + 0.5 for p in selected_path]
        py = [p[1] + 0.5 for p in selected_path]
        ax.plot(px, py, color="#10B981", linewidth=4.5, linestyle="-", label=f"Selected Route ({selected_resp_id})", zorder=4)
        
    # Plot Responders
    for r_info in responders_info:
        r_id = r_info["responder_id"]
        r_pos = DEMO_GRID_LOCATIONS.get(r_id, (0, 0))
        rx, ry = r_pos
        
        if r_id == selected_resp_id:
            # Selected responder: DARK BLUE
            ax.scatter(rx + 0.5, ry + 0.5, s=350, color=THEME_COLORS["dark_blue"], edgecolors="#FFFFFF", linewidth=2, zorder=5)
            ax.text(rx + 0.5, ry + 0.5, r_id, color="#FFFFFF", fontsize=8, fontweight="bold", ha="center", va="center", zorder=6)
        else:
            # Other responders: LIGHT BLUE
            ax.scatter(rx + 0.5, ry + 0.5, s=250, color=THEME_COLORS["active_blue"], edgecolors="#FFFFFF", linewidth=1.5, zorder=5)
            ax.text(rx + 0.5, ry + 0.5, r_id, color="#FFFFFF", fontsize=7, ha="center", va="center", zorder=6)
            
    # Plot Incident: RED Marker
    ix, iy = incident_pos
    ax.scatter(ix + 0.5, iy + 0.5, s=450, color=THEME_COLORS["emergency_red"], edgecolors="#FFFFFF", linewidth=2.5, marker="*", zorder=6)
    ax.text(ix + 0.5, iy + 0.85, f"EMERGENCY ({incident_id})", color=THEME_COLORS["emergency_red"], fontsize=9, fontweight="bold", ha="center", va="center", zorder=7)
    
    # Grid formatting & axes coordinates
    ax.set_xlim(0, GRID_WIDTH)
    ax.set_ylim(0, GRID_HEIGHT)
    ax.set_xticks([i + 0.5 for i in range(GRID_WIDTH)])
    ax.set_xticklabels([str(i) for i in range(GRID_WIDTH)], fontsize=9, fontweight="bold", color=THEME_COLORS["text"])
    ax.set_yticks([i + 0.5 for i in range(GRID_HEIGHT)])
    ax.set_yticklabels([str(i) for i in range(GRID_HEIGHT)], fontsize=9, fontweight="bold", color=THEME_COLORS["text"])
    
    ax.set_xlabel("Grid X Coordinates (Research Simulation)", fontsize=10, fontweight="bold", color=THEME_COLORS["dark_blue"])
    ax.set_ylabel("Grid Y Coordinates (Research Simulation)", fontsize=10, fontweight="bold", color=THEME_COLORS["dark_blue"])
    ax.set_title(f"A* Route Planning Grid (10×10) — Incident {incident_id}", fontsize=12, fontweight="bold", color=THEME_COLORS["dark_blue"], pad=12)
    
    # Custom legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, frameon=True, facecolor="#FFFFFF", edgecolor=THEME_COLORS["border"])
    
    plt.tight_layout()
    return fig
