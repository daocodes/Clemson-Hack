import datetime
import os
from flask import Flask, render_template, request, jsonify
from google import genai
import ee

app = Flask(__name__)
PROJECT_ID = "deft-cove-474115-j1"
API_KEY = "AIzaSyDjN3wQtKA3BWuQVyeQSJdMwui7kao4-Rg"

ee.Initialize(project=PROJECT_ID)

client = genai.Client(api_key=API_KEY)

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

# Function to return coordinates
def get_coordinates(lat, lng):
    return {"lat": lat, "lng": lng}

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

@app.route("/describe", methods=["GET"])
def describe():
    polarization = request.args.get("polarization", "VV")
    mode = request.args.get("mode", "IW")
    print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Request: polarization={polarization}, mode={mode}")
    
    prompt = f"Describe a Sentinel-1 SAR image with polarization {polarization} in mode {mode}."
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return jsonify({"description": response.text})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"description": f"Error generating description: {e}"})



@app.route("/clicked")
def clicked():
    try:
        lat = float(request.args.get("lat"))
        lng = float(request.args.get("lng"))
        coords = get_coordinates(str(lat), str(lng))
        return jsonify(coords)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid coordinates"}), 400

if __name__ == "__main__":
    app.run(debug=True)
