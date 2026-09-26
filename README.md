# Intelligent Emergency Dispatch System 🚨

**B.Tech Computer Engineering Final Year Research Prototype**  
*Hyperdimensional Computing (HDC) + Constraint Satisfaction Problem (CSP) + A* 10×10 Grid Pathfinder + SQLite + Google Maps Handoff*

---

## 📌 Executive Overview

The **Intelligent Emergency Dispatch System** is an academic/research prototype designed to optimize emergency responder selection and dynamic routing. The system processes emergency messages, prioritizes incidents based on urgency scores, filters candidate responders using **Hyperdimensional Computing (HDC)** in $D=10,000$ vector space, enforces hard domain rules via **Constraint Satisfaction Problems (CSP)**, evaluates shortest spatial routes using **A* Pathfinding** on a 10×10 research grid, and persists all operational records in a physical **SQLite** database (`emergency_dispatch.db`).

---

## 🏗️ System Architecture & Execution Pipeline

```
                 EMERGENCY MESSAGE
                         │
                 INCIDENT DETECTOR
                         │
                      SQLITE
                         │
              INCIDENT PRIORITY QUEUE
                         │
                  HDC SCREENING
                         │
                  CSP VALIDATION
                         │
                  A* ROUTING (10x10 Grid)
                         │
                 RESPONDER SELECTED
                         │
              EXPLAINABLE DASHBOARD
                         │
                  DISPATCH SAVED
                         │
               NEXT EMERGENCY / RE-PLANNING
```

---

## 🔬 Core Algorithm Components

### 1. HDC Candidate Screening (`hdc_screener.py`)
- **Dimension:** $D = 10,000$ Bipolar Vector Symbolic Architecture ($\{-1, +1\}$ vectors).
- **Function:** Encodes incident requirements and responder attributes into hypervectors. Computes runtime cosine similarity to produce a dynamic candidate shortlist.
- **Role:** Fast, noise-tolerant candidate screening (soft filtering). Does NOT enforce hard binary rules.

### 2. CSP Constraint Validation (`csp_validator.py`)
- **Scope:** Evaluates ONLY HDC-shortlisted responders.
- **Constraints:**
  1. *Vehicle Type Compatibility* (e.g. `FIRE` → `fire_truck`, `rescue_unit`)
  2. *Capacity Rule* ($\text{Responder Capacity} \ge \text{Incident Severity}$)
  3. *Availability Lock* ($\text{Availability} == 1$)
- **Role:** Hard logical validation with explicit rejection rationales.

### 3. A* Route Planning (`astar_router.py`)
- **Grid:** $10 \times 10$ Research Grid with obstacle coordinates.
- **Heuristic:** Manhattan Distance $h(x, y) = |x_1 - x_2| + |y_1 - y_2|$.
- **Role:** Spatial path planning and route cost optimization among valid candidates.

### 4. Dynamic Re-planning (`replanner.py`)
- **Triggers:** `RESPONDER_UNAVAILABLE`, `ROUTE_BLOCKED`, `LOCATION_CHANGED`.
- **Role:** Automatically reruns the pipeline when an assigned responder fails, recording audit logs in `route_updates`.

---

## 🔑 Crucial Academic Distinction

| Feature | Research Grid (10×10 A*) | Google Maps Navigation |
|---|---|---|
| **Purpose** | Spatial algorithm research & visualization | Real-world driver navigation handoff |
| **Coordinates** | Abstract grid coordinates $(x, y) \in [0..9] \times [0..9]$ | Physical database address strings |
| **Execution** | Matplotlib rendering in Python | External browser launch via URL |

---

## 🗄️ SQLite Database Schema (`database.py`)

Database File: `emergency_dispatch.db` (Physical, Persistent)

1. `messages`: Raw incoming emergency reports.
2. `incidents`: Processed incidents with severity & priority status.
3. `responders`: Fleet database (vehicle type, depot location, availability).
4. `dispatches`: Active dispatch assignments.
5. `processing_results`: Full audit trail of HDC similarity, CSP pass/fail, and A* costs.
6. `route_updates`: Dynamic re-planning change logs.

---

## 🚀 How to Run the Application

### 1. Install Dependencies
```bash
pip install -r emergency_dispatch_system/requirements.txt
```

### 2. Launch Streamlit Application
```bash
streamlit run app.py
```

### 3. Run Benchmark Evaluation Script
```bash
python emergency_dispatch_system/evaluate.py
```
