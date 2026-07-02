import json
import os

# Note: Adjust the import below to match your specific ADK implementation.
# Using a generic representation of Agent, Task, and Environment primitives for A2A.
from adk import Agent, Task, Environment

# ------------------------------------------------------------------
# Configuration — swap this path when your real GWR file is ready
# ------------------------------------------------------------------
DATA_FILE = os.path.join(os.path.dirname(__file__), "hcmc_gwr_output.geojson")

# ------------------------------------------------------------------
# 1. Data Agent  — reads GWR output from a local MCP-served data file
# ------------------------------------------------------------------
class DataAgent(Agent):
    def __init__(self, name="Data_Agent"):
        super().__init__(name=name)

    def execute(self, task: Task):
        print(f"[{self.name}] Reading GWR spatial dataset from: {DATA_FILE}")

        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(
                f"GWR data file not found: {DATA_FILE}\n"
                "Please place your GeoJSON file at that path or update DATA_FILE."
            )

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        n_features = len(geojson_data.get("features", []))
        print(f"[{self.name}] Loaded {n_features} GWR features for Ho Chi Minh City.")

        # A2A: inject payload into shared task context
        task.context["geojson_payload"] = geojson_data
        task.context["data_file"]       = DATA_FILE
        print(f"[{self.name}] Payload ready. Passing to WebGIS_Agent...")

        return task


# ------------------------------------------------------------------
# 2. WebGIS Agent  — generates Flask + Leaflet app from GWR payload
# ------------------------------------------------------------------
class WebGISAgent(Agent):
    def __init__(self, name="WebGIS_Agent"):
        super().__init__(name=name)

    def execute(self, task: Task):
        print(f"[{self.name}] Receiving GWR payload from Data_Agent...")

        geojson_data = task.context.get("geojson_payload")
        if not geojson_data:
            raise ValueError("No GeoJSON payload received from Data_Agent.")

        print(f"[{self.name}] Generating WebGIS application files (app.py, index.html)...")

        os.makedirs("templates", exist_ok=True)
        self._create_app_py(geojson_data)
        self._create_index_html()

        print(
            f"[{self.name}] WebGIS application successfully generated.\n"
            f"  >> Run 'python app.py' to start the local server, then open http://127.0.0.1:5000"
        )
        return task

    # ── Flask backend ──────────────────────────────────────────────
    def _create_app_py(self, geojson_data):
        """Creates the local Flask server to host the GWR WebGIS app."""
        app_py_content = f"""from flask import Flask, render_template, jsonify

app = Flask(__name__)

# GWR payload for Ho Chi Minh City — passed from Data_Agent via A2A
GEOJSON_DATA = {json.dumps(geojson_data, indent=4)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    return jsonify(GEOJSON_DATA)

if __name__ == '__main__':
    approval = input('Do you approve the deployment of this WebGIS map? (Y/N): ')
    if approval.strip().lower() == 'y':
        app.run(debug=True, port=5000)
    else:
        print('Deployment aborted by human-in-the-loop safeguard.')
"""
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(app_py_content)

    # ── Leaflet frontend ───────────────────────────────────────────
    def _create_index_html(self):
        """Creates the Leaflet choropleth frontend per SKILL.md GWR guidelines."""
        index_html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HCMC Land Surface Temperature — GWR Analysis</title>
    <meta name="description" content="Interactive WebGIS map showing Geographically Weighted Regression outputs for Land Surface Temperature in Ho Chi Minh City.">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

    <style>
        /* ── Base ──────────────────────────────────────────── */
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #111; }

        /* ── Map ───────────────────────────────────────────── */
        #map { width: 100vw; height: 100vh; }

        /* ── Title overlay ─────────────────────────────────── */
        #title-bar {
            position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
            z-index: 1000; background: rgba(15,15,15,0.82); backdrop-filter: blur(8px);
            color: #f0f0f0; padding: 10px 22px; border-radius: 24px;
            font-size: 15px; font-weight: 600; letter-spacing: 0.3px;
            border: 1px solid rgba(255,255,255,0.12); pointer-events: none;
            white-space: nowrap;
        }

        /* ── Legend ────────────────────────────────────────── */
        .legend {
            background: rgba(255,255,255,0.95); padding: 12px 16px;
            border-radius: 8px; line-height: 1.9; font-size: 13px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.35);
        }
        .legend h4 { margin: 0 0 8px; font-size: 13px; font-weight: 700;
                     color: #222; text-align: center; }
        .legend i  { width: 18px; height: 14px; display: inline-block;
                     margin-right: 7px; border-radius: 3px; vertical-align: middle; }

        /* ── Popup ─────────────────────────────────────────── */
        .gwr-popup { font-family: 'Segoe UI', Arial, sans-serif; min-width: 210px; }
        .gwr-popup h3 { margin: 0 0 8px; font-size: 14px; color: #1a1a2e;
                        border-bottom: 2px solid #e74c3c; padding-bottom: 4px; }
        .gwr-popup table { border-collapse: collapse; font-size: 12px; width: 100%; }
        .gwr-popup td { padding: 3px 5px; }
        .gwr-popup td:first-child { color: #555; width: 55%; }
        .gwr-popup td:last-child  { font-weight: 600; color: #111; text-align: right; }
        .gwr-popup tr:nth-child(even) td { background: #f9f9f9; border-radius: 3px; }
    </style>
</head>
<body>

    <div id="title-bar">🌡️ Ho Chi Minh City — Land Surface Temperature (GWR)</div>
    <div id="map"></div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        // ── 1. Colour scale: blue → yellow → red (LST-driven) ──
        function getColor(lst) {
            return lst > 38   ? '#a50026' :
                   lst > 36.5 ? '#d73027' :
                   lst > 35   ? '#f46d43' :
                   lst > 33.5 ? '#fdae61' :
                   lst > 32   ? '#ffffbf' :
                   lst > 30.5 ? '#abd9e9' :
                                '#313695';
        }

        // ── 2. Initialise map centred on Ho Chi Minh City ──────
        const map = L.map('map', { zoomControl: true }).setView([10.76, 106.69], 10);

        // ArcGIS World Dark Gray Base — template uses {z}/{y}/{x} ordering
        L.tileLayer(
            'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
            {
                maxZoom: 16,
                attribution: 'Tiles &copy; <a href="https://www.esri.com">Esri</a> | World Dark Gray Base'
            }
        ).addTo(map);

        // ── 3. Fetch GWR data and build choropleth ─────────────
        fetch('/api/data')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                const geoLayer = L.geoJSON(data, {
                    // Choropleth style driven by predicted LST
                    style: feature => ({
                        fillColor:   getColor(feature.properties.lst_predicted),
                        fillOpacity: 0.78,
                        color:       '#ffffff',
                        weight:      1.5
                    }),

                    onEachFeature: (feature, layer) => {
                        const p = feature.properties;

                        // Rich interactive popup with all GWR fields
                        const popupContent = `
                            <div class="gwr-popup">
                                <h3>${p.district || 'Unknown District'}</h3>
                                <table>
                                    <tr><td>🌡️ Predicted LST</td><td><b>${p.lst_predicted} °C</b></td></tr>
                                    <tr><td>📊 Local R²</td><td>${p.local_r2}</td></tr>
                                    <tr><td>📐 Residual</td><td>${p.residual} °C</td></tr>
                                    <tr><td>🌿 Coeff NDVI</td><td>${p.coeff_ndvi}</td></tr>
                                    <tr><td>🏗️ Coeff Impervious</td><td>${p.coeff_impervious}</td></tr>
                                    <tr><td>💧 Coeff Water Dist.</td><td>${p.coeff_water_dist}</td></tr>
                                </table>
                            </div>
                        `;
                        layer.bindPopup(popupContent, { maxWidth: 260 });

                        // Hover highlight effects
                        layer.on('mouseover', () => layer.setStyle({ fillOpacity: 0.95, weight: 2.5, color: '#333' }));
                        layer.on('mouseout',  () => layer.setStyle({ fillOpacity: 0.78, weight: 1.5, color: '#fff' }));
                    }
                }).addTo(map);

                // Auto-fit map to data extent
                map.fitBounds(geoLayer.getBounds(), { padding: [30, 30] });
            })
            .catch(err => console.error('Error fetching GWR GeoJSON:', err));

        // ── 4. Legend ──────────────────────────────────────────
        const legend = L.control({ position: 'bottomright' });
        legend.onAdd = function () {
            const div    = L.DomUtil.create('div', 'legend');
            const grades = [29, 30.5, 32, 33.5, 35, 36.5, 38];
            const labels = grades.map((g, i) =>
                `<i style="background:${getColor(g + 0.1)}"></i>` +
                `${g}${grades[i + 1] ? ' – ' + grades[i + 1] : '+'} °C`
            );
            div.innerHTML = '<h4>LST Predicted</h4>' + labels.join('<br>');
            return div;
        };
        legend.addTo(map);
    </script>

</body>
</html>
"""
        with open("templates/index.html", "w", encoding="utf-8") as f:
            f.write(index_html_content)


# ------------------------------------------------------------------
# 3. Agent2Agent (A2A) — orchestration pipeline
# ------------------------------------------------------------------
def run_multi_agent_system():
    data_agent   = DataAgent()
    webgis_agent = WebGISAgent()

    shared_task = Task(description="Read HCMC GWR output and build WebGIS application")

    env = Environment()
    env.add_agent(data_agent)
    env.add_agent(webgis_agent)

    print("=" * 60)
    print("  HCMC WebGIS Multi-Agent System  |  GWR / LST Analysis")
    print("=" * 60)

    # A2A step 1: Data_Agent reads and injects the GWR payload
    task_after_data = data_agent.execute(shared_task)

    # A2A step 2: WebGIS_Agent builds the app from the payload
    webgis_agent.execute(task_after_data)

    print("-" * 60)
    print("Pipeline complete. Run:  python app.py")
    print("-" * 60)


if __name__ == "__main__":
    run_multi_agent_system()
