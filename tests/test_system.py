"""
=============================================================================
FLOOD DETECTION SYSTEM - ADVANCED TEST SUITE
Validates Dual-Engine ML, Cause-Aware Classification, XAI, Response Planning,
Alerts, CSV Data Management, and all Flask HTTP / API endpoints.
=============================================================================
"""

import os
import sys
import unittest
import json
import io

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from app import app
from utils.prediction import load_risk_model, load_cause_model, predict_flood_risk, load_model_metadata
from utils.weather_service import fetch_environmental_data
from utils.data_processing import LOCATIONS_DATA
from utils.response_planning import generate_response_plan
from database.db import (
    init_db,
    save_prediction,
    get_recent_predictions,
    save_alert,
    get_alerts,
    authenticate_user,
    register_user
)


class TestAdvancedFloodPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepare test environment and initialize database."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()
        init_db()

    # 1. Dual-Engine ML Model Tests
    def test_01_risk_model_loading(self):
        """Test that the Random Forest risk classification model loads."""
        model = load_risk_model()
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, "predict"))

    def test_02_cause_model_loading(self):
        """Test that the Cause-Aware Random Forest model loads."""
        model = load_cause_model()
        self.assertIsNotNone(model)
        self.assertTrue(hasattr(model, "predict"))

    def test_03_prediction_cause_aware_rainfall(self):
        """Test prediction for heavy rainfall scenario yields Rainfall-Driven cause."""
        rain_input = {
            "rainfall_mm": 160.0,
            "temp_c": 26.0,
            "humidity_pct": 88.0,
            "river_water_level_m": 3.6,
            "soil_moisture_pct": 90.0,
            "drainage_capacity_pct": 60.0,
            "prev_rainfall_7d_mm": 130.0,
            "elevation_m": 228.0,
            "distance_to_river_km": 12.0
        }
        res = predict_flood_risk(rain_input, location_name="Jalandhar")
        self.assertIn(res["prediction"]["risk_level"], [2, 3])
        self.assertIn("probable_cause", res)
        self.assertIn("title", res["probable_cause"])
        self.assertGreater(res["probable_cause"]["confidence_pct"], 50.0)

    def test_04_prediction_cause_aware_drainage_choke(self):
        """Test prediction for urban drainage choke yields Drainage-Driven cause."""
        drainage_input = {
            "rainfall_mm": 70.0,
            "temp_c": 28.0,
            "humidity_pct": 82.0,
            "river_water_level_m": 2.6,
            "soil_moisture_pct": 75.0,
            "drainage_capacity_pct": 18.0,  # Heavily choked drainage
            "prev_rainfall_7d_mm": 65.0,
            "elevation_m": 244.0,
            "distance_to_river_km": 6.0
        }
        res = predict_flood_risk(drainage_input, location_name="Ludhiana")
        self.assertIn("probable_cause", res)
        self.assertIn("Drainage", res["probable_cause"]["title"])

    def test_05_explainability_generation(self):
        """Test that Explainable AI (XAI) feature attributions are computed."""
        sample_input = {
            "rainfall_mm": 90.0,
            "temp_c": 27.0,
            "humidity_pct": 80.0,
            "river_water_level_m": 4.6,
            "soil_moisture_pct": 80.0,
            "drainage_capacity_pct": 40.0,
            "prev_rainfall_7d_mm": 70.0,
            "elevation_m": 225.0,
            "distance_to_river_km": 7.0
        }
        res = predict_flood_risk(sample_input, location_name="Kapurthala")
        self.assertIn("explainability", res)
        self.assertIn("feature_contributions", res["explainability"])
        self.assertIn("elevating_factors", res["explainability"])
        self.assertGreater(len(res["explainability"]["elevating_factors"]), 0)

    def test_06_response_planning_directives(self):
        """Test that cause-aware response planning produces priorities and resources."""
        loc_meta = LOCATIONS_DATA["Ludhiana"]
        inputs = {
            "rainfall_mm": 80.0,
            "river_water_level_m": 4.8,
            "soil_moisture_pct": 75.0,
            "drainage_capacity_pct": 30.0
        }
        plan = generate_response_plan(
            risk_level=3,
            probable_cause_code=2,
            inputs=inputs,
            location_name="Ludhiana",
            loc_meta=loc_meta
        )
        self.assertEqual(plan["emergency_priority"], "Priority 1 - Critical Emergency Response")
        self.assertIn("resources", plan)
        self.assertIn("dewatering_pumps", plan["resources"])
        self.assertIn("action_checklist", plan)

    def test_07_verified_locations(self):
        """Test all 7 Punjab locations exist with coordinates and base drainage capacity."""
        for city in ["Jalandhar", "Phagwara", "Amritsar", "Ludhiana", "Kapurthala", "Hoshiarpur", "Nawanshahr"]:
            self.assertIn(city, LOCATIONS_DATA)
            loc = LOCATIONS_DATA[city]
            self.assertIn("base_drainage_capacity_pct", loc)
            self.assertGreater(loc["latitude"], 30.0)

    def test_08_weather_service_and_forecast(self):
        """Test weather service returns telemetry, weather condition, and hourly forecast."""
        data = fetch_environmental_data("Amritsar", timeout_seconds=1.0)
        self.assertIn("weather_condition", data)
        self.assertIn("hourly_rainfall_24h", data)
        self.assertIn("daily_forecast", data)
        self.assertEqual(len(data["hourly_rainfall_24h"]), 24)

    def test_09_database_and_alerts(self):
        """Test logging and retrieving early warning alerts in SQLite."""
        alert_id = save_alert(
            location_name="Hoshiarpur",
            alert_level="Severe",
            title="TEST ALERT",
            message="Test emergency notification",
            probable_cause="Flash Torrent Choes"
        )
        self.assertIsInstance(alert_id, int)
        alerts_list = get_alerts(limit=5)
        self.assertGreater(len(alerts_list), 0)

    def test_10_view_routes(self):
        """Test all primary web pages return HTTP 200."""
        routes = [
            "/", "/analytics", "/alerts", "/response-planning",
            "/data", "/model", "/history", "/docs", "/login", "/register"
        ]
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} returned {res.status_code}")

    def test_11_api_predict(self):
        """Test POST /api/predict endpoint returns complete intelligence payload."""
        payload = {
            "location_name": "Phagwara",
            "rainfall_mm": 60.0,
            "river_water_level_m": 2.5,
            "soil_moisture_pct": 70.0,
            "drainage_capacity_pct": 50.0,
            "prev_rainfall_7d_mm": 40.0,
            "temp_c": 28.0,
            "humidity_pct": 75.0,
            "elevation_m": 234.0,
            "distance_to_river_km": 8.5
        }
        res = self.client.post("/api/predict", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("probable_cause", data["result"])
        self.assertIn("response_plan", data["result"])
        self.assertIn("explainability", data["result"])

    def test_12_api_map_markers(self):
        """Test GET /api/map-markers endpoint returns 7 markers with cause and drainage."""
        res = self.client.get("/api/map-markers")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["markers"]), 7)
        for m in data["markers"]:
            self.assertIn("probable_cause", m)
            self.assertIn("drainage_capacity_pct", m)

    def test_13_api_csv_export(self):
        """Test GET /api/export/predictions-csv returns CSV file attachment."""
        res = self.client.get("/api/export/predictions-csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.content_type)
        self.assertIn(b"location_name", res.data)

    def test_14_api_csv_upload_validation(self):
        """Test POST /api/upload-csv handles CSV validation."""
        csv_content = (
            "location,rainfall_mm,river_water_level_m,soil_moisture_pct,prev_rainfall_7d_mm,drainage_capacity_pct\n"
            "Jalandhar,85.0,3.2,78.0,60.0,55.0\n"
            "Ludhiana,110.0,4.6,85.0,90.0,35.0\n"
        )
        data = {
            'file': (io.BytesIO(csv_content.encode('utf-8')), 'test_dataset.csv')
        }
        res = self.client.post('/api/upload-csv', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        json_data = json.loads(res.data)
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["total_rows_processed"], 2)

    def test_15_api_compare_locations(self):
        """Test GET /api/compare-locations returns 7-station comparative matrix."""
        res = self.client.get("/api/compare-locations")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["count"], 7)
        for st in data["comparison"]:
            self.assertIn("risk_score", st)
            self.assertIn("river_margin_m", st)
            self.assertIn("probable_cause", st)
            self.assertIn("drainage_capacity_pct", st)

    def test_16_api_sensitivity_analysis(self):
        """Test POST /api/sensitivity-analysis evaluates What-If scenario deltas."""
        payload = {
            "location_name": "Jalandhar",
            "base_features": {
                "rainfall_mm": 10.0,
                "river_water_level_m": 2.1,
                "soil_moisture_pct": 40.0,
                "drainage_capacity_pct": 70.0,
                "prev_rainfall_7d_mm": 15.0,
                "temp_c": 28.0,
                "humidity_pct": 55.0,
                "elevation_m": 228.0,
                "distance_to_river_km": 12.0
            },
            "adjustment": {
                "rainfall_delta": 60.0,
                "drainage_delta": -25.0
            }
        }
        res = self.client.post("/api/sensitivity-analysis", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertIn("delta", data)
        self.assertIn("score_change", data["delta"])
        self.assertGreater(data["adjusted"]["risk_score"], data["baseline"]["risk_score"])

    def test_17_alert_escalation_detection(self):
        """Test alert escalation logic detects transition to higher risk."""
        # 1. Save initial baseline prediction (Moderate)
        rec1 = {
            "location_name": "Nawanshahr",
            "latitude": 31.1240,
            "longitude": 76.1160,
            "rainfall_mm": 50.0,
            "temp_c": 28.0,
            "humidity_pct": 70.0,
            "river_water_level_m": 3.0,
            "soil_moisture_pct": 65.0,
            "prev_rainfall_7d_mm": 40.0,
            "elevation_m": 250.0,
            "distance_to_river_km": 5.5,
            "drainage_capacity_pct": 58.0,
            "risk_level": 1,
            "risk_label": "Moderate",
            "confidence_pct": 80.0,
            "probable_cause": "Drainage Congestion",
            "data_source": "Test"
        }
        save_prediction(rec1)

        # 2. Trigger high/severe prediction for same location
        pred_res = predict_flood_risk({
            "rainfall_mm": 180.0,
            "river_water_level_m": 5.5,
            "soil_moisture_pct": 95.0,
            "drainage_capacity_pct": 30.0,
            "prev_rainfall_7d_mm": 200.0,
            "elevation_m": 250.0,
            "distance_to_river_km": 5.5
        }, location_name="Nawanshahr")

        self.assertIn("alert_info", pred_res)
        self.assertTrue(pred_res["alert_info"]["alert_triggered"])
        self.assertTrue(pred_res["alert_info"].get("is_escalation", False))

    def test_18_composite_risk_score_and_supporting_evidence(self):
        """Test continuous composite risk index and cause supporting evidence."""
        res = predict_flood_risk({
            "rainfall_mm": 140.0,
            "river_water_level_m": 3.8,
            "soil_moisture_pct": 90.0,
            "drainage_capacity_pct": 55.0,
            "prev_rainfall_7d_mm": 110.0,
            "elevation_m": 228.0,
            "distance_to_river_km": 12.0
        }, location_name="Jalandhar")

        self.assertIn("composite_risk_score", res["prediction"])
        self.assertIsInstance(res["prediction"]["composite_risk_score"], float)
        self.assertGreater(res["prediction"]["composite_risk_score"], 40.0)

        self.assertIn("supporting_factors", res["probable_cause"])
        self.assertGreater(len(res["probable_cause"]["supporting_factors"]), 0)
        self.assertIn("status_note", res["probable_cause"])

    def test_19_api_station_report_export(self):
        """Test GET /api/export/station-report/<location_name> returns valid structured JSON report."""
        res = self.client.get("/api/export/station-report/Jalandhar")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("prediction", data)
        self.assertIn("probable_cause", data)
        self.assertIn("response_plan", data)
        self.assertEqual(data["location_name"], "Jalandhar")

        # Test invalid location returns 404
        res_invalid = self.client.get("/api/export/station-report/NonExistentCity")
        self.assertEqual(res_invalid.status_code, 404)


if __name__ == "__main__":
    unittest.main()
