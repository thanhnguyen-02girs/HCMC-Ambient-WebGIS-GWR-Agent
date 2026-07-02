---
name: webgis-agent
description: >
  Parses GeoJSON (including Geographically Weighted Regression outputs) and
  configures Leaflet map layers with choropleth styling and interactive popups.
  Specialised for spatial analysis results such as Land Surface Temperature (LST)
  variations across Ho Chi Minh City.
---

# WebGIS Agent Skill

This skill provides instructions and examples for parsing GeoJSON data —
including **GWR (Geographically Weighted Regression) outputs** — and
visualising it on an interactive Leaflet map with:

- **Choropleth polygon fills** coloured by Predicted LST (blue → red).
- **Interactive popups** showing all GWR fields per feature.

---

## GWR Data Schema

When the Data_Agent passes a GWR GeoJSON payload, each feature's
`properties` object is expected to contain the following fields:

| Field | Description | Unit |
|---|---|---|
| `district` | District / zone label | string |
| `lst_predicted` | Predicted Land Surface Temperature | °C |
| `local_r2` | Local goodness-of-fit (0–1) | dimensionless |
| `residual` | Observed minus predicted LST | °C |
| `coeff_ndvi` | Local GWR coefficient for NDVI | — |
| `coeff_impervious` | Local GWR coefficient for impervious surface | — |
| `coeff_water_dist` | Local GWR coefficient for distance to water | — |

> **Note:** When you swap in your real GWR output file, make sure it contains
> these exact property names, or update the popup template below accordingly.

---

## Instructions

Follow these steps when building the WebGIS application for GWR / LST data:

### 1. Parse and Validate GWR GeoJSON
- Load the GeoJSON file (e.g., `hcmc_gwr_output.geojson`) from disk or via
  the Flask `/api/data` endpoint.
- Confirm the `FeatureCollection` has `features` with `Polygon` geometries.
- Extract the full range of `lst_predicted` values across all features to
  compute the **colour scale domain** (min → max) for the choropleth.

### 2. Build the LST Colour Scale
- Use a **blue → yellow → red** sequential gradient to encode LST intensity:
  - Cool (< 32 °C) → `#313695`
  - Moderate (≈ 35 °C) → `#ffffbf`
  - Hot (> 38 °C) → `#a50026`
- Implement a `getColor(lst)` helper function using breakpoints derived from
  the actual data range so the scale is always data-driven.

### 3. Initialise the Leaflet Map
- Centre the map on Ho Chi Minh City: `[10.76, 106.69]`, zoom `10`.
- Add an OpenStreetMap base tile layer for geographic context.

### 4. Add GWR Choropleth Layer
- Use `L.geoJSON()` with two options:
  - **`style`**: Set `fillColor` using `getColor(feature.properties.lst_predicted)`,
    `fillOpacity: 0.75`, `weight: 1.5`, `color: '#fff'`.
  - **`onEachFeature`**: Bind a rich popup and add hover highlight events
    (`mouseover` / `mouseout` to lighten/darken the fill).

### 5. Popup Content Template
Each popup must display **all GWR fields** in a structured card:

```html
<div class="gwr-popup">
  <h3>{district}</h3>
  <table>
    <tr><td>🌡️ Predicted LST</td><td><b>{lst_predicted} °C</b></td></tr>
    <tr><td>📊 Local R²</td><td>{local_r2}</td></tr>
    <tr><td>📐 Residual</td><td>{residual} °C</td></tr>
    <tr><td>🌿 Coeff NDVI</td><td>{coeff_ndvi}</td></tr>
    <tr><td>🏗️ Coeff Impervious</td><td>{coeff_impervious}</td></tr>
    <tr><td>💧 Coeff Water Dist.</td><td>{coeff_water_dist}</td></tr>
  </table>
</div>
```

### 6. Add a Legend
- Render a fixed-position `L.control` legend showing the LST colour ramp with
  labelled breakpoints so users can interpret the choropleth without hovering.

---

## Full Reference Implementation

```javascript
// ── Colour scale (blue → yellow → red, data-driven) ──────────────
function getColor(lst) {
    return lst > 38   ? '#a50026' :
           lst > 36.5 ? '#d73027' :
           lst > 35   ? '#f46d43' :
           lst > 33.5 ? '#fdae61' :
           lst > 32   ? '#ffffbf' :
           lst > 30.5 ? '#abd9e9' :
                        '#313695';
}

// ── Map initialisation (Ho Chi Minh City) ─────────────────────────
const map = L.map('map').setView([10.76, 106.69], 10);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// ── GWR GeoJSON layer ─────────────────────────────────────────────
fetch('/api/data')
    .then(r => r.json())
    .then(data => {
        L.geoJSON(data, {
            style: feature => ({
                fillColor:   getColor(feature.properties.lst_predicted),
                fillOpacity: 0.75,
                color:       '#ffffff',
                weight:      1.5
            }),
            onEachFeature: (feature, layer) => {
                const p = feature.properties;
                layer.bindPopup(`
                    <div class="gwr-popup">
                        <h3>${p.district}</h3>
                        <table>
                            <tr><td>🌡️ Predicted LST</td><td><b>${p.lst_predicted} °C</b></td></tr>
                            <tr><td>📊 Local R²</td><td>${p.local_r2}</td></tr>
                            <tr><td>📐 Residual</td><td>${p.residual} °C</td></tr>
                            <tr><td>🌿 Coeff NDVI</td><td>${p.coeff_ndvi}</td></tr>
                            <tr><td>🏗️ Coeff Impervious</td><td>${p.coeff_impervious}</td></tr>
                            <tr><td>💧 Coeff Water Dist.</td><td>${p.coeff_water_dist}</td></tr>
                        </table>
                    </div>
                `);
                // Hover highlight
                layer.on('mouseover', () => layer.setStyle({ fillOpacity: 0.95, weight: 2.5 }));
                layer.on('mouseout',  () => layer.setStyle({ fillOpacity: 0.75, weight: 1.5 }));
            }
        }).addTo(map);
    })
    .catch(err => console.error('Error fetching GWR data:', err));

// ── Legend control ────────────────────────────────────────────────
const legend = L.control({ position: 'bottomright' });
legend.onAdd = function () {
    const div    = L.DomUtil.create('div', 'legend');
    const grades = [29, 30.5, 32, 33.5, 35, 36.5, 38];
    div.innerHTML = '<h4>LST (°C)</h4>';
    grades.forEach((g, i) => {
        div.innerHTML +=
            `<i style="background:${getColor(g + 0.1)}"></i>` +
            `${g}${grades[i + 1] ? '–' + grades[i + 1] : '+'}<br>`;
    });
    return div;
};
legend.addTo(map);
```

### Legend CSS (add to `<style>`)
```css
.legend { background: white; padding: 10px 14px; border-radius: 6px;
          line-height: 1.8; font-size: 13px; box-shadow: 0 1px 5px rgba(0,0,0,.3); }
.legend h4 { margin: 0 0 6px; font-size: 14px; }
.legend i  { width: 16px; height: 16px; display: inline-block;
             margin-right: 6px; border-radius: 2px; vertical-align: middle; }
.gwr-popup h3 { margin: 0 0 6px; font-size: 14px; color: #333; }
.gwr-popup table { border-collapse: collapse; font-size: 12px; }
.gwr-popup td { padding: 2px 6px; }
.gwr-popup td:first-child { color: #555; }
.gwr-popup td:last-child  { font-weight: 500; color: #111; }
```

---

## Swapping in Your Real GWR File

When your real GWR output is ready, update the `DATA_FILE` path in
`multi_agent.py` (inside `DataAgent.execute`):

```python
# Change this line in DataAgent.execute():
DATA_FILE = r"C:\path\to\your\real_gwr_output.geojson"
```

The rest of the pipeline requires **no further changes** as long as the
property names match the schema above.
