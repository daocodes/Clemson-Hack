import os
from flask import Flask, render_template, request, jsonify
from google import genai
import ee

app = Flask(__name__)

ee.Initialize(project='lucid-fountain-466101-v0')

client = genai.Client(api_key="AIzaSyDjN3wQtKA3BWuQVyeQSJdMwui7kao4-Rg")

MODEL_NAME = "gemini-2.5-flash"

def get_tile_url(polarization="VV", mode="IW"):
    point = ee.Geometry.Point([-90.0715, 29.9511])
    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(point)
        .filterDate("2023-06-01", "2023-06-30")
        .filter(ee.Filter.eq("instrumentMode", mode))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", polarization))
    )
    image = collection.first()
    if not image:
        return None
    vis_params = {"bands": ["VV"], "min": -25, "max": 0}
    try:
        map_id_dict = ee.Image(image).getMapId(vis_params)
        return map_id_dict["tile_fetcher"].url_format
    except Exception as e:
        print("Error generating tile URL:", e)
        return None

@app.route("/")
def index():
    polarization = request.args.get("polarization", "VV")
    mode = request.args.get("mode", "IW")
    tile_url = get_tile_url(polarization, mode)
    message = ""
    if not tile_url:
        message = "No image found for the selected polarization/mode."
    return render_template(
        "index.html",
        tile_url=tile_url or "",
        polarization=polarization,
        mode=mode,
        message=message,
    )

@app.route("/describe")
def describe():
    polarization = request.args.get("polarization", "VV")
    mode = request.args.get("mode", "IW")
    prompt = f"Describe a Sentinel-1 SAR image with polarization {polarization} in mode {mode}."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        description = response.text
        return jsonify({"description": description})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"description": f"Error generating Gemini description: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
