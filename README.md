# 🌡️ Ambient WebGIS Agent: Spec-Driven Urban Heat Island & Morphology Analyzer

**Track:** Freestyle Track  
**Domain:** Geographic Information Systems (GIS) / Spatial Data Science  

## 🎥 System Demonstration Video
> **Watch the 60-second end-to-end runtime (A2A -> Human-in-the-Loop -> Leaflet Render):**  
> 🔗 [Click here to view the Live Demo on Google Drive](https://drive.google.com/file/d/1r8g4oD-9eHERfgRkHHnx3cNfVAH2ttUI/view?usp=sharing)


## 📖 Project Overview
Analyzing the micro-local impacts of urban morphology on Land Surface Temperature (LST) typically requires heavy desktop GIS software and manual statistical workflows. **Ambient WebGIS Agent** transforms this into an automated, ambient multi-agent pipeline. 

Focused on the metropolitan area of **Ho Chi Minh City (Vietnam)**, this system ingests Geographically Weighted Regression (GWR) spatial outputs, dynamically compiles a Python backend, and vibe-codes an interactive Leaflet mapping client—bridging raw spatial statistics with web-based decision-making.

---

## 🧠 The 3 Core Course Concepts Demonstrated

### 1. Multi-Agent System (via ADK)
The workflow is governed by a decentralized two-agent architecture:
* **`Data_Agent`**: Ingests and parses localized GeoJSON payloads containing GWR regression coefficients (NDVI, built-up density, Local R²).
* **`WebGIS_Agent`**: Receives the spatial payload via A2A (Agent-to-Agent) communication and dynamically compiles the presentation layer (`app.py` Flask server + `index.html` Leaflet client).

### 2. Portable Agent Skills (`SKILL.md`)
To prevent "context rot" during UI generation, the cartographic logic is strictly isolated within a dedicated `SKILL.md` directory. The skill equips the agent with domain-specific mapping rules:
* Auto-generating a Choropleth layer mapped to *Predicted LST*.
* Binding feature popups specifically to localized regression coefficients.
* Instantiating a multi-basemap toggle (CartoDB Dark Matter vs. Esri World Imagery).

### 3. Continuous Effective Trust (Human-in-the-Loop Safeguard)
Adhering to the 7-pillar zero-trust architecture, code is treated as disposable while human governance remains absolute. Before the asynchronous runtime deploys the Flask server to open port `5000`, the execution trajectory hits an intentional hard breakpoint:
```text
[Security Guard] Deployment paused. Inspect generated GWR layers? Approve launch? (Y/N):

# 1. Extract the submission package
cd WebGIS_Capstone_Package

# 2. Install dependencies
pip install flask

# 3. Trigger the multi-agent runtime
python multi_agent.py

# 4. Authorize the ambient breakpoint when prompted in terminal: [ Y ]
# 5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000)