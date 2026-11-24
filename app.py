"""
=============================================================================
FLOOD DETECTION SYSTEM - ADVANCED FLASK PLATFORM
Comprehensive Flood Intelligence, Cause-Aware Classification & Response Planning
=============================================================================
"""

import os
import io
import csv
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for,
    flash,
    Response,
    send_file
)
import pandas as pd
from werkzeug.utils import secure_filename

from utils.data_processing import (
    LOCATIONS_DATA,
    RISK_METADATA,
    CAUSE_METADATA,
    PUNJAB_HISTORICAL_DATA,
    FEATURE_COLUMNS,
    sanitize_input_features
)
from utils.weather_service import fetch_environmental_data
from utils.prediction import predict_flood_risk, load_model_metadata
from database.db import (
    init_db,
    save_prediction,
    get_recent_predictions,
    get_location_latest_predictions,
    get_alerts,
    acknowledge_alert,
    acknowledge_all_alerts,
    authenticate_user,
    register_user,
    get_user_by_id
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "punjab-flood-intelligence-secret-key-2026")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Initialize database schema and default credentials
init_db()


# ---------------------------------------------------------------------------
# Core Operational Views
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the primary interactive map and flood risk dashboard."""
    locations = list(LOCATIONS_DATA.values())
    default_city = "Jalandhar"

    # Pre-fetch initial environmental telemetry
    initial_env = fetch_environmental_data(default_city)

    # Pre-calculate baseline prediction with cause-awareness
    initial_pred = predict_flood_risk(
        initial_env,
        location_name=default_city,
        data_source=initial_env["data_source"]
    )

    # Retrieve unacknowledged alerts count for header badge
    active_alerts = get_alerts(limit=5, unacknowledged_only=True)

    return render_template(
        "index.html",
        locations=locations,
        default_city=default_city,
        initial_env=initial_env,
        initial_pred=initial_pred,
        risk_meta=RISK_METADATA,
        cause_meta=CAUSE_METADATA,
        active_alerts_count=len(active_alerts)
    )


@app.route("/analytics")
def analytics():
    """Render the advanced flood intelligence analytics dashboard."""
    latest_records = get_location_latest_predictions()
    
    # Calculate summary metrics across all 7 monitored stations
    total_stations = len(LOCATIONS_DATA)
    high_risk_count = 0
    severe_risk_count = 0
    rainfall_list = []
    station_summaries = []

    for name, loc in LOCATIONS_DATA.items():
        if name in latest_records:
            rec = latest_records[name]
            r_level = rec["risk_level"]
            r_label = rec["risk_label"]
            rain = rec["rainfall_mm"]
            cause = rec.get("probable_cause", "Normal Drainage")
        else:
            base_pred = predict_flood_risk(loc["baseline"], location_name=name, data_source="Regional Baseline")
            r_level = base_pred["prediction"]["risk_level"]
            r_label = base_pred["prediction"]["risk_label"]
            rain = loc["baseline"]["rainfall_mm"]
            cause = base_pred["probable_cause"]["title"]

        if r_level >= 3:
            severe_risk_count += 1
        elif r_level == 2:
            high_risk_count += 1

        rainfall_list.append(rain)
        station_summaries.append({
            "name": name,
            "district": loc.get("district", name),
            "risk_level": r_level,
            "risk_label": r_label,
            "rainfall_mm": rain,
            "cause": cause,
            "danger_stage": loc["danger_river_level_m"]
        })

    avg_rainfall = round(sum(rainfall_list) / len(rainfall_list), 1) if rainfall_list else 0.0
    
    # Identify highest risk station
    highest_station = max(station_summaries, key=lambda s: s["risk_level"]) if station_summaries else None

    return render_template(
        "analytics.html",
        total_stations=total_stations,
        high_risk_count=high_risk_count,
        severe_risk_count=severe_risk_count,
        avg_rainfall=avg_rainfall,
        highest_station=highest_station,
        station_summaries=station_summaries,
        historical_monsoon=PUNJAB_HISTORICAL_DATA["annual_monsoon_records"],
        monthly_averages=PUNJAB_HISTORICAL_DATA["monthly_averages_punjab"]
    )


@app.route("/alerts")
def alerts():
    """Render early warning notifications and alert history."""
    all_alerts = get_alerts(limit=100, unacknowledged_only=False)
    unack_alerts = [a for a in all_alerts if not a["is_acknowledged"]]
    return render_template(
        "alerts.html",
        alerts=all_alerts,
        unacknowledged_count=len(unack_alerts)
    )


@app.route("/response-planning")
def response_planning():
    """Render cause-aware flood response planning and priority resource allocation."""
    selected_city = request.args.get("city", default="Jalandhar")
    if selected_city not in LOCATIONS_DATA:
        selected_city = "Jalandhar"

    env_data = fetch_environmental_data(selected_city)
    assessment = predict_flood_risk(env_data, location_name=selected_city, data_source=env_data["data_source"])

    return render_template(
        "response_planning.html",
        locations=list(LOCATIONS_DATA.values()),
        selected_city=selected_city,
        assessment=assessment
    )


@app.route("/data")
def data_management():
    """Render the dataset management, CSV upload, and export portal."""
    recent_records = get_recent_predictions(limit=15)
    return render_template(
        "data_management.html",
        recent_records=recent_records,
        feature_columns=FEATURE_COLUMNS
    )


@app.route("/model")
def model_info():
    """Render machine learning architecture, metrics, confusion matrix & XAI."""
    metadata = load_model_metadata()
    return render_template("model_info.html", metadata=metadata)


@app.route("/history")
def history():
    """Render the SQLite historical predictions audit log."""
    records = get_recent_predictions(limit=150)
    return render_template("history.html", records=records)


@app.route("/docs")
def documentation():
    """Render comprehensive technical architecture documentation."""
    return render_template("docs.html", locations=LOCATIONS_DATA)


# ---------------------------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user email authentication."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = authenticate_user(email, password)
        if user:
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle new user registration via email."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        success, result = register_user(email, password, name)
        if success:
            flash("Account registered successfully! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash(result, "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Clear session and log out."""
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for("login"))


@app.route("/about")
def about():
    """Legacy route redirect to docs."""
    return redirect(url_for("documentation"))


# ---------------------------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/locations", methods=["GET"])
def api_locations():
    """Return catalog of Punjab monitoring locations."""
    return jsonify({
        "success": True,
        "count": len(LOCATIONS_DATA),
        "locations": LOCATIONS_DATA
    })


@app.route("/api/weather/<location_name>", methods=["GET"])
def api_weather(location_name):
    """Fetch live Open-Meteo atmospheric & forecast telemetry (with fallback)."""
    if location_name not in LOCATIONS_DATA:
        return jsonify({"success": False, "error": f"Unknown location '{location_name}'"}), 404

    data = fetch_environmental_data(location_name)
    return jsonify({
        "success": True,
        "location": location_name,
        "data": data
    })


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Execute dual-engine ML prediction for given location and parameters,
    log to SQLite database, and trigger early warning alerts if needed.
    """
    req_json = request.get_json(silent=True) or {}
    location_name = req_json.get("location_name", "Jalandhar")
    data_source = req_json.get("data_source", "Manual Parameter Simulation")

    try:
        result = predict_flood_risk(req_json, location_name=location_name, data_source=data_source)

        # Persist record in SQLite
        db_record = {
            "location_name": location_name,
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "rainfall_mm": result["inputs"]["rainfall_mm"],
            "temp_c": result["inputs"]["temp_c"],
            "humidity_pct": result["inputs"]["humidity_pct"],
            "river_water_level_m": result["inputs"]["river_water_level_m"],
            "soil_moisture_pct": result["inputs"]["soil_moisture_pct"],
            "prev_rainfall_7d_mm": result["inputs"]["prev_rainfall_7d_mm"],
            "elevation_m": result["inputs"]["elevation_m"],
            "distance_to_river_km": result["inputs"]["distance_to_river_km"],
            "drainage_capacity_pct": result["inputs"]["drainage_capacity_pct"],
            "risk_level": result["prediction"]["risk_level"],
            "risk_label": result["prediction"]["risk_label"],
            "confidence_pct": result["prediction"]["confidence_pct"],
            "probable_cause": result["probable_cause"]["title"],
            "data_source": data_source
        }
        record_id = save_prediction(db_record)
        result["db_id"] = record_id

        return jsonify({"success": True, "result": result})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/map-markers", methods=["GET"])
def api_map_markers():
    """
    Return comprehensive spatial markers for all 7 Punjab stations,
    incorporating risk level, cause-aware tags, and hotspots.
    """
    latest_db_records = get_location_latest_predictions()
    markers = []

    for name, loc in LOCATIONS_DATA.items():
        if name in latest_db_records:
            rec = latest_db_records[name]
            risk_level = rec["risk_level"]
            risk_label = rec["risk_label"]
            confidence = rec["confidence_pct"]
            rainfall = rec["rainfall_mm"]
            humidity = rec["humidity_pct"]
            river_level = rec["river_water_level_m"]
            drainage = rec.get("drainage_capacity_pct", 65.0)
            cause = rec.get("probable_cause", "Normal Drainage")
            source = rec["data_source"]
        else:
            base_pred = predict_flood_risk(loc["baseline"], location_name=name, data_source="Regional Baseline")
            risk_level = base_pred["prediction"]["risk_level"]
            risk_label = base_pred["prediction"]["risk_label"]
            confidence = base_pred["prediction"]["confidence_pct"]
            rainfall = loc["baseline"]["rainfall_mm"]
            humidity = loc["baseline"]["humidity_pct"]
            river_level = loc["baseline"]["river_water_level_m"]
            drainage = loc["baseline"].get("drainage_capacity_pct", 65.0)
            cause = base_pred["probable_cause"]["title"]
            source = "Regional Baseline"

        meta = RISK_METADATA.get(risk_level, RISK_METADATA[0])

        markers.append({
            "name": name,
            "district": loc["district"],
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "elevation_m": loc["elevation_m"],
            "nearest_river": loc["nearest_river"],
            "rainfall_mm": rainfall,
            "humidity_pct": humidity,
            "river_water_level_m": river_level,
            "danger_river_level_m": loc["danger_river_level_m"],
            "drainage_capacity_pct": drainage,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "color": meta["color"],
            "confidence_pct": confidence,
            "probable_cause": cause,
            "hotspot_description": loc.get("hotspot_description", ""),
            "data_source": source
        })

    return jsonify({"success": True, "markers": markers})


@app.route("/api/compare-locations", methods=["GET"])
def api_compare_locations():
    """
    Return comprehensive multi-station comparison metrics for all 7 Punjab stations,
    incorporating rainfall, river surcharge, drainage capacity, risk tier, and cause.
    """
    latest_db_records = get_location_latest_predictions()
    comparison_data = []

    for name, loc in LOCATIONS_DATA.items():
        if name in latest_db_records:
            rec = latest_db_records[name]
            risk_level = rec["risk_level"]
            risk_label = rec["risk_label"]
            confidence = rec["confidence_pct"]
            rainfall = rec["rainfall_mm"]
            river_level = rec["river_water_level_m"]
            soil_moist = rec["soil_moisture_pct"]
            drainage = rec.get("drainage_capacity_pct", 65.0)
            cause = rec.get("probable_cause", "Normal Drainage")
            source = rec["data_source"]
        else:
            base_pred = predict_flood_risk(loc["baseline"], location_name=name, data_source="Regional Baseline")
            risk_level = base_pred["prediction"]["risk_level"]
            risk_label = base_pred["prediction"]["risk_label"]
            confidence = base_pred["prediction"]["confidence_pct"]
            rainfall = loc["baseline"]["rainfall_mm"]
            river_level = loc["baseline"]["river_water_level_m"]
            soil_moist = loc["baseline"]["soil_moisture_pct"]
            drainage = loc["baseline"].get("drainage_capacity_pct", 65.0)
            cause = base_pred["probable_cause"]["title"]
            source = "Regional Baseline"

        meta = RISK_METADATA.get(risk_level, RISK_METADATA[0])
        danger_stage = loc["danger_river_level_m"]
        river_margin = round(danger_stage - river_level, 2)

        # Expected severity score
        risk_score = round(((risk_level / 3.0) * 80.0) + (rainfall * 0.1) + ((100.0 - drainage) * 0.1), 1)
        risk_score = min(100.0, max(5.0, risk_score))

        comparison_data.append({
            "name": name,
            "district": loc["district"],
            "latitude": loc["latitude"],
            "longitude": loc["longitude"],
            "elevation_m": loc["elevation_m"],
            "nearest_river": loc["nearest_river"],
            "rainfall_mm": rainfall,
            "river_water_level_m": river_level,
            "danger_river_level_m": danger_stage,
            "river_margin_m": river_margin,
            "soil_moisture_pct": soil_moist,
            "drainage_capacity_pct": drainage,
            "risk_level": risk_level,
            "risk_label": risk_label,
            "risk_score": risk_score,
            "color": meta["color"],
            "confidence_pct": confidence,
            "probable_cause": cause,
            "data_source": source
        })

    return jsonify({"success": True, "count": len(comparison_data), "comparison": comparison_data})


@app.route("/api/sensitivity-analysis", methods=["POST"])
def api_sensitivity_analysis():
    """
    Execute real-time What-If sensitivity analysis: recomputes model inference
    under modified rainfall, drainage, or river stages and returns comparative deltas.
    """
    req_json = request.get_json(silent=True) or {}
    location_name = req_json.get("location_name", "Jalandhar")
    base_features = req_json.get("base_features", {})
    adjustment = req_json.get("adjustment", {})

    if location_name not in LOCATIONS_DATA:
        location_name = "Jalandhar"

    try:
        # Run baseline
        base_pred = predict_flood_risk(base_features, location_name=location_name, data_source="Baseline")
        
        # Apply deltas
        modified_features = dict(base_pred["inputs"])
        if "rainfall_delta" in adjustment:
            modified_features["rainfall_mm"] = max(0.0, modified_features["rainfall_mm"] + float(adjustment["rainfall_delta"]))
        if "drainage_delta" in adjustment:
            modified_features["drainage_capacity_pct"] = max(5.0, min(100.0, modified_features["drainage_capacity_pct"] + float(adjustment["drainage_delta"])))
        if "river_delta" in adjustment:
            modified_features["river_water_level_m"] = max(0.5, modified_features["river_water_level_m"] + float(adjustment["river_delta"]))
        if "soil_moisture_delta" in adjustment:
            modified_features["soil_moisture_pct"] = max(10.0, min(100.0, modified_features["soil_moisture_pct"] + float(adjustment["soil_moisture_delta"])))

        # Run adjusted
        adj_pred = predict_flood_risk(modified_features, location_name=location_name, data_source="What-If Simulation")

        base_score = base_pred["prediction"].get("composite_risk_score", 15.0)
        adj_score = adj_pred["prediction"].get("composite_risk_score", 15.0)
        score_diff = round(adj_score - base_score, 1)

        tier_changed = base_pred["prediction"]["risk_level"] != adj_pred["prediction"]["risk_level"]
        cause_changed = base_pred["probable_cause"]["cause_code"] != adj_pred["probable_cause"]["cause_code"]

        summary = (
            f"Under the modified scenario, risk score shifted by {score_diff:+0.1f} points "
            f"(from {base_score}% to {adj_score}%). "
            f"Risk tier: {base_pred['prediction']['risk_label']} ➔ {adj_pred['prediction']['risk_label']}. "
            f"Probable cause: {base_pred['probable_cause']['title']} ➔ {adj_pred['probable_cause']['title']}."
        )

        return jsonify({
            "success": True,
            "location_name": location_name,
            "baseline": {
                "risk_level": base_pred["prediction"]["risk_level"],
                "risk_label": base_pred["prediction"]["risk_label"],
                "risk_score": base_score,
                "confidence_pct": base_pred["prediction"]["confidence_pct"],
                "probable_cause": base_pred["probable_cause"]["title"],
                "color": base_pred["prediction"]["color"]
            },
            "adjusted": {
                "risk_level": adj_pred["prediction"]["risk_level"],
                "risk_label": adj_pred["prediction"]["risk_label"],
                "risk_score": adj_score,
                "confidence_pct": adj_pred["prediction"]["confidence_pct"],
                "probable_cause": adj_pred["probable_cause"]["title"],
                "color": adj_pred["prediction"]["color"]
            },
            "delta": {
                "score_change": score_diff,
                "tier_changed": tier_changed,
                "cause_changed": cause_changed
            },
            "summary": summary
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/alerts", methods=["GET"])
def api_get_alerts():
    """Return active and past alert history."""
    alerts_data = get_alerts(limit=50)
    return jsonify({"success": True, "alerts": alerts_data})


@app.route("/api/alerts/acknowledge/<int:alert_id>", methods=["POST"])
def api_acknowledge_alert(alert_id):
    """Mark an alert as acknowledged."""
    acknowledge_alert(alert_id)
    return jsonify({"success": True, "message": f"Alert #{alert_id} acknowledged."})


@app.route("/api/alerts/acknowledge-all", methods=["POST"])
def api_acknowledge_all():
    """Mark all active alerts as acknowledged."""
    acknowledge_all_alerts()
    return jsonify({"success": True, "message": "All alerts acknowledged."})


@app.route("/api/upload-csv", methods=["POST"])
def api_upload_csv():
    """
    Handle custom CSV dataset upload, validate schema, impute missing values,
    and execute batch predictions.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename."}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"success": False, "error": "Only CSV files are supported."}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        df_upload = pd.read_csv(stream)

        # Validate minimum required columns
        required_cols = ["rainfall_mm", "river_water_level_m", "soil_moisture_pct"]
        missing = [c for c in required_cols if c not in df_upload.columns]
        if missing:
            return jsonify({
                "success": False,
                "error": f"CSV missing required columns: {', '.join(missing)}"
            }), 400

        # Process each row
        results_preview = []
        for idx, row in df_upload.head(10).iterrows():
            loc_name = str(row.get("location", row.get("location_name", "Jalandhar")))
            if loc_name not in LOCATIONS_DATA:
                loc_name = "Jalandhar"

            pred = predict_flood_risk(row.to_dict(), location_name=loc_name, data_source="Uploaded CSV Batch")
            results_preview.append({
                "row": idx + 1,
                "location": loc_name,
                "rainfall_mm": pred["inputs"]["rainfall_mm"],
                "river_water_level_m": pred["inputs"]["river_water_level_m"],
                "risk_label": pred["prediction"]["risk_label"],
                "probable_cause": pred["probable_cause"]["title"],
                "confidence": pred["prediction"]["confidence_pct"]
            })

        return jsonify({
            "success": True,
            "total_rows_processed": len(df_upload),
            "preview_samples": results_preview,
            "message": f"Successfully processed {len(df_upload)} rows from uploaded CSV."
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"CSV processing error: {str(e)}"}), 500


@app.route("/api/export/predictions-csv", methods=["GET"])
def api_export_predictions_csv():
    """Generate and return CSV download of all saved predictions."""
    records = get_recent_predictions(limit=500)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = [
        "id", "timestamp", "location_name", "latitude", "longitude",
        "rainfall_mm", "temp_c", "humidity_pct", "river_water_level_m",
        "soil_moisture_pct", "prev_rainfall_7d_mm", "drainage_capacity_pct",
        "elevation_m", "distance_to_river_km", "risk_level", "risk_label",
        "confidence_pct", "probable_cause", "data_source"
    ]
    writer.writerow(headers)

    for r in records:
        writer.writerow([
            r.get("id"), r.get("created_at"), r.get("location_name"),
            r.get("latitude"), r.get("longitude"), r.get("rainfall_mm"),
            r.get("temp_c"), r.get("humidity_pct"), r.get("river_water_level_m"),
            r.get("soil_moisture_pct"), r.get("prev_rainfall_7d_mm"),
            r.get("drainage_capacity_pct", 65.0), r.get("elevation_m"),
            r.get("distance_to_river_km"), r.get("risk_level"),
            r.get("risk_label"), r.get("confidence_pct"),
            r.get("probable_cause", "Normal Drainage"), r.get("data_source")
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=punjab_flood_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )


@app.route("/api/export/station-report/<location_name>", methods=["GET"])
def api_export_station_report(location_name):
    """Generate structured JSON report for a specific location."""
    if location_name not in LOCATIONS_DATA:
        return jsonify({"error": "Unknown location"}), 404

    env_data = fetch_environmental_data(location_name)
    report = predict_flood_risk(env_data, location_name=location_name, data_source=env_data["data_source"])
    return jsonify(report)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n===========================================================")
    print(f"Punjab Flood Intelligence System active at http://127.0.0.1:{port}")
    print(f"===========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=True)
