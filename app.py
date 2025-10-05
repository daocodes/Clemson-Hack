import datetime
import os
import traceback

import ee
from flask import Flask, jsonify, render_template, request, send_file
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


def get_tile_url(lat, lng, polarization="VV", mode="IW", start_date="2023-06-01", end_date="2025-10-04"):
    """Return a map tile URL for the specified polarization, mode, date range, and coordinates."""
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
        .filterDate(start_date, end_date)
        .filter(ee.Filter.eq("instrumentMode", mode))
        .filter(ee.Filter.listContains("transmitterReceiverPolarisation", polarization))
        .sort('system:time_start', False)  # Sort by date descending (most recent first)
    )

    image = collection.first()  # Now this gets the MOST RECENT image
    if not image:
        app.logger.debug(
            "No SAR image found for the given filters at %s,%s for dates %s to %s",
            lat_f, lng_f, start_date, end_date
        )
        return None

    vis_params = {"bands": [polarization], "min": -25, "max": 0}
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

    # Handle date slider - convert days from start to actual dates
    days_from_start = request.args.get("days_from_start")
    start_date = "2014-10-01"  # Fixed start date (Sentinel-1 launch)

    if days_from_start:
        try:
            days = int(days_from_start)
            from datetime import datetime, timedelta
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=days)
            end_date = end_dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            end_date = "2025-10-04"
            days_from_start = 3164
    else:
        end_date = "2025-10-04"
        days_from_start = 3164

    app.logger.info(
        "Analysis request: pol=%s mode=%s lat=%s lng=%s dates=%s to %s (days=%s)",
        polarization,
        mode,
        latBig,
        lngBig,
        start_date,
        end_date,
        days_from_start,
    )

    # Call get_tile_url with date parameters
    tile_url = get_tile_url(latBig, lngBig, polarization, mode, start_date, end_date)

    message = ""
    if not tile_url:
        message = "No image found for the selected polarization/mode/date range."

    return render_template(
        "analysis.html",
        tile_url=tile_url or "",
        lat=latBig,
        lng=lngBig,
        polarization=polarization,
        mode=mode,
        start_date=start_date,
        end_date=end_date,
        days_from_start=days_from_start,
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


@app.route("/get_tile_url")
def get_tile_url_endpoint():
    """API endpoint to get tile URL dynamically without page reload."""
    polarization = request.args.get("polarization", "VV")
    lat = request.args.get("lat")
    lng = request.args.get("lng")
    mode = request.args.get("mode", "IW")
    days_from_start = request.args.get("days_from_start")

    start_date = "2014-10-01"

    if days_from_start:
        try:
            days = int(days_from_start)
            from datetime import datetime, timedelta
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=days)
            end_date = end_dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            end_date = "2025-10-04"
    else:
        end_date = "2025-10-04"

    tile_url = get_tile_url(lat, lng, polarization, mode, start_date, end_date)

    return jsonify({
        "tile_url": tile_url,
        "start_date": start_date,
        "end_date": end_date,
        "success": tile_url is not None
    })


@app.route("/incidents.csv")
def incidents_csv():
    """Serve the incidents.csv file from the project directory."""
    csv_path = os.path.join(os.path.dirname(__file__), "incidents.csv")
    if os.path.exists(csv_path):
        return send_file(csv_path, mimetype='text/csv')
    else:
        return "incidents.csv not found", 404


@app.route("/")
def index():
    # Use default coordinates (Gulf of Mexico) if none provided
    latBig = request.args.get("lat", "29.9511")
    lngBig = request.args.get("lng", "-90.0715")
    polarization = request.args.get("polarization", "VV")
    mode = request.args.get("mode", "IW")

    # Handle date slider - convert days from start to actual dates
    days_from_start = request.args.get("days_from_start")
    start_date = "2014-10-01"  # Fixed start date (Sentinel-1 launch)

    if days_from_start:
        try:
            days = int(days_from_start)
            from datetime import datetime, timedelta
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=days)
            end_date = end_dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            end_date = "2025-10-04"
            days_from_start = 3164
    else:
        end_date = "2025-10-04"
        days_from_start = 3164

    app.logger.info(
        "Index request: pol=%s mode=%s lat=%s lng=%s dates=%s to %s (days=%s)",
        polarization,
        mode,
        latBig,
        lngBig,
        start_date,
        end_date,
        days_from_start,
    )

    # Call get_tile_url with date parameters and default coordinates
    tile_url = get_tile_url(latBig, lngBig, polarization, mode, start_date, end_date)

    message = ""
    if not tile_url:
        message = "No image found for the selected polarization/mode/date range."

    return render_template(
        "analysis.html",
        tile_url=tile_url or "",
        lat=latBig,
        lng=lngBig,
        polarization=polarization,
        mode=mode,
        start_date=start_date,
        end_date=end_date,
        days_from_start=days_from_start,
        message=message,
    )


@app.route("/subscribe", methods=["POST"])
def subscribe():
    """Handle subscription requests for location-based alerts."""
    try:
        data = request.get_json()
        email = data.get('email')
        lat = data.get('lat')
        lon = data.get('lon')

        if not email or '@' not in email:
            return jsonify({'success': False, 'message': 'Invalid email address'}), 400

        if lat is None or lon is None:
            return jsonify({'success': False, 'message': 'Invalid coordinates'}), 400

        # Store subscription in CSV file
        import csv
        subscribers_file = os.path.join(os.path.dirname(__file__), 'subscribers.csv')

        # Check if file exists, if not create with headers
        file_exists = os.path.exists(subscribers_file)

        with open(subscribers_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['email', 'lat', 'lon', 'timestamp'])
            writer.writerow([email, lat, lon, datetime.datetime.now().isoformat()])

        app.logger.info(f"New subscription: {email} at ({lat}, {lon})")

        return jsonify({
            'success': True,
            'message': f'Successfully subscribed {email} to alerts for location ({lat}, {lon})'
        })

    except Exception as e:
        app.logger.exception("Error processing subscription")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing your subscription'
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
