import datetime
import os
import traceback

import ee
from flask import Flask, jsonify, render_template, request
from google import genai

app = Flask(__name__)
PROJECT_ID = "deft-cove-474115-j1"
API_KEY = "AIzaSyDjN3wQtKA3BWuQVyeQSJdMwui7kao4-Rg"

# --- Try to initialize Earth Engine but don't let it kill the app ---
EE_OK = False
try:
    ee.Initialize(project=PROJECT_ID)
    EE_OK = True
    app.logger.info("Earth Engine initialized.")
except Exception as e:
    EE_OK = False
    app.logger.warning("Earth Engine init failed (continuing without EE): %s", e)

# GenAI client (keep as before)
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"


def get_tile_url(lat, lng, polarization="VV", mode="IW"):
    """Return a map tile URL for the specified polarization, mode, and coordinates."""
    if not EE_OK:
        app.logger.warning("get_tile_url called but Earth Engine not initialized.")
        return None

    if lat is None or lng is None:
        app.logger.debug("Missing lat/lng: lat=%r lng=%r", lat, lng)
        return None

    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (ValueError, TypeError) as e:
        app.logger.debug("Invalid lat/lng: %s (%s, %s)", e, lat, lng)
        return None

    # Earth Engine expects [lon, lat]
    point = ee.Geometry.Point([lng_f, lat_f])

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(point)
        .filterDate("2023-06-01", "2023-06-30")
        .filter(ee.Filter.eq("instrumentMode", mode))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", polarization))
    )

    image = collection.first()
    if not image:
        app.logger.debug(
            "No SAR image found for the given filters at %s,%s", lat_f, lng_f
        )
        return None

    vis_params = {"bands": ["VV"], "min": -25, "max": 0}
    try:
        map_id_dict = ee.Image(image).getMapId(vis_params)
        return map_id_dict["tile_fetcher"].url_format
    except Exception as e:
        app.logger.exception("Error generating tile URL")
        return None


@app.route("/analysis")
def analysis():
    polarization = request.args.get("polarization", "VV")
    latBig = request.args.get("lat")
    lngBig = request.args.get("lng")
    mode = request.args.get("mode", "IW")

    app.logger.info(
        "Analysis request: pol=%s mode=%s lat=%s lng=%s",
        polarization,
        mode,
        latBig,
        lngBig,
    )

    # ---- FIX: call get_tile_url with correct params ----
    # Use positional call or correct keyword names
    tile_url = get_tile_url(latBig, lngBig, polarization, mode)

    message = ""
    if not tile_url:
        message = "No image found for the selected polarization/mode."

    return render_template(
        "analysis.html",
        tile_url=tile_url or "",
        lat=latBig,
        lng=lngBig,
        polarization=polarization,
        mode=mode,
        message=message,
    )


@app.route("/describe", methods=["GET"])
def describe():
    polarization = request.args.get("polarization", "VV")
    mode = request.args.get("mode", "IW")
    prompt = f"Describe a Sentinel-1 SAR image with polarization {polarization} in mode {mode}."
    app.logger.info("Describe request: pol=%s mode=%s", polarization, mode)

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)

        # Try several fields the SDK might expose
        text = None
        if hasattr(response, "text") and response.text:
            text = response.text
        elif hasattr(response, "candidates") and response.candidates:
            first = response.candidates[0]
            if isinstance(first, dict):
                text = first.get("content") or first.get("text") or str(first)
            else:
                text = (
                    getattr(first, "content", None)
                    or getattr(first, "text", None)
                    or str(first)
                )
        elif hasattr(response, "output"):
            text = getattr(response, "output")
        else:
            app.logger.debug("GenAI response repr: %r", response)
            app.logger.debug("GenAI response dir: %s", dir(response))
            return (
                jsonify(
                    {
                        "description": None,
                        "error": "No text found in genai response",
                        "debug": {"repr": repr(response), "dir": dir(response)},
                    }
                ),
                500,
            )

        app.logger.info("GenAI returned text length=%d", len(text) if text else 0)
        return jsonify({"description": text})

    except Exception as e:
        app.logger.exception("Error generating Gemini description")
        return jsonify({"description": None, "error": str(e)}), 500


@app.route("/historical")
def historical():
    return render_template("historical.html")


@app.route("/")
def index():
    # If you want root to forward to analysis preserving no lat/lng:
    return render_template("analysis.html")


if __name__ == "__main__":
    app.run(debug=True)
