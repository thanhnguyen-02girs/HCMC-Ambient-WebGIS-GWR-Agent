from flask import Flask, render_template, jsonify

app = Flask(__name__)

# GWR payload for Ho Chi Minh City — passed from Data_Agent via A2A
GEOJSON_DATA = {
    "type": "FeatureCollection",
    "name": "HCMC_GWR_Output",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": [
        {
            "type": "Feature",
            "properties": {
                "district": "District 1 (Ben Nghe)",
                "lst_predicted": 38.4,
                "local_r2": 0.81,
                "residual": -0.6,
                "coeff_ndvi": -1.92,
                "coeff_impervious": 2.31,
                "coeff_water_dist": -0.47
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.694,
                            10.773
                        ],
                        [
                            106.705,
                            10.773
                        ],
                        [
                            106.705,
                            10.782
                        ],
                        [
                            106.694,
                            10.782
                        ],
                        [
                            106.694,
                            10.773
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "district": "District 3 (Vo Thi Sau)",
                "lst_predicted": 36.9,
                "local_r2": 0.76,
                "residual": 0.3,
                "coeff_ndvi": -1.74,
                "coeff_impervious": 2.05,
                "coeff_water_dist": -0.38
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.679,
                            10.775
                        ],
                        [
                            106.69,
                            10.775
                        ],
                        [
                            106.69,
                            10.785
                        ],
                        [
                            106.679,
                            10.785
                        ],
                        [
                            106.679,
                            10.775
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "district": "Binh Thanh District",
                "lst_predicted": 35.2,
                "local_r2": 0.7,
                "residual": 1.1,
                "coeff_ndvi": -1.55,
                "coeff_impervious": 1.88,
                "coeff_water_dist": -0.55
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.7,
                            10.8
                        ],
                        [
                            106.72,
                            10.8
                        ],
                        [
                            106.72,
                            10.818
                        ],
                        [
                            106.7,
                            10.818
                        ],
                        [
                            106.7,
                            10.8
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "district": "Thu Duc City (Linh Trung)",
                "lst_predicted": 32.7,
                "local_r2": 0.62,
                "residual": -1.4,
                "coeff_ndvi": -2.1,
                "coeff_impervious": 1.43,
                "coeff_water_dist": -0.71
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.74,
                            10.84
                        ],
                        [
                            106.77,
                            10.84
                        ],
                        [
                            106.77,
                            10.87
                        ],
                        [
                            106.74,
                            10.87
                        ],
                        [
                            106.74,
                            10.84
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "district": "Binh Chanh District (Peri-urban)",
                "lst_predicted": 34.1,
                "local_r2": 0.58,
                "residual": 0.8,
                "coeff_ndvi": -1.3,
                "coeff_impervious": 1.62,
                "coeff_water_dist": -0.29
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.58,
                            10.72
                        ],
                        [
                            106.63,
                            10.72
                        ],
                        [
                            106.63,
                            10.76
                        ],
                        [
                            106.58,
                            10.76
                        ],
                        [
                            106.58,
                            10.72
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "district": "Can Gio District (Mangrove)",
                "lst_predicted": 29.3,
                "local_r2": 0.88,
                "residual": -0.2,
                "coeff_ndvi": -2.85,
                "coeff_impervious": 0.71,
                "coeff_water_dist": -1.2
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.85,
                            10.4
                        ],
                        [
                            106.95,
                            10.4
                        ],
                        [
                            106.95,
                            10.5
                        ],
                        [
                            106.85,
                            10.5
                        ],
                        [
                            106.85,
                            10.4
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {
                "district": "District 12 (Industrial Zone)",
                "lst_predicted": 39.1,
                "local_r2": 0.79,
                "residual": 1.6,
                "coeff_ndvi": -1.45,
                "coeff_impervious": 2.67,
                "coeff_water_dist": -0.22
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            106.63,
                            10.855
                        ],
                        [
                            106.665,
                            10.855
                        ],
                        [
                            106.665,
                            10.885
                        ],
                        [
                            106.63,
                            10.885
                        ],
                        [
                            106.63,
                            10.855
                        ]
                    ]
                ]
            }
        }
    ]
}

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
