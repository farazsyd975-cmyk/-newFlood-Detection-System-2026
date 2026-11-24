"""
=============================================================================
FLOOD DETECTION SYSTEM - ADVANCED ENVIRONMENTAL & WEATHER SERVICE
Integrates with Open-Meteo API for real-time atmospheric observations,
WMO weather codes, 24-hour hourly trends, and multi-day forecasts with robust
fail-safe offline fallback to verified Punjab regional baselines.
=============================================================================
"""

import requests
from utils.data_processing import LOCATIONS_DATA

WMO_WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    62: "Moderate Rain",
    63: "Heavy Rain",
    65: "Torrential Downpour",
    80: "Slight Rain Showers",
    81: "Moderate Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Severe Thunderstorm with Heavy Hail"
}


def get_weather_desc(code):
    return WMO_WEATHER_CODES.get(int(code), "Overcast / Rain")


def fetch_environmental_data(location_name="Jalandhar", timeout_seconds=3.0):
    """
    Fetch comprehensive atmospheric and forecast data from Open-Meteo or fall
    back to calibrated Punjab regional baseline data.
    """
    if location_name not in LOCATIONS_DATA:
        location_name = "Jalandhar"

    loc = LOCATIONS_DATA[location_name]
    lat = loc["latitude"]
    lon = loc["longitude"]

    # Base return dictionary (offline baseline)
    result = {
        "location_name": location_name,
        "latitude": lat,
        "longitude": lon,
        "elevation_m": loc["elevation_m"],
        "distance_to_river_km": loc["distance_to_river_km"],
        "nearest_river": loc["nearest_river"],
        "normal_river_level_m": loc["normal_river_level_m"],
        "danger_river_level_m": loc["danger_river_level_m"],
        "rainfall_mm": loc["baseline"]["rainfall_mm"],
        "temp_c": loc["baseline"]["temp_c"],
        "humidity_pct": loc["baseline"]["humidity_pct"],
        "river_water_level_m": loc["baseline"]["river_water_level_m"],
        "soil_moisture_pct": loc["baseline"]["soil_moisture_pct"],
        "prev_rainfall_7d_mm": loc["baseline"]["prev_rainfall_7d_mm"],
        "drainage_capacity_pct": loc["baseline"].get("drainage_capacity_pct", 65.0),
        "weather_condition": "Partly Cloudy (Baseline)",
        "weather_code": 2,
        "hourly_rainfall_24h": [round(float(loc["baseline"]["rainfall_mm"] / 24.0), 2)] * 24,
        "hourly_time_labels": [f"{h:02d}:00" for h in range(24)],
        "daily_forecast": [
            {"day": "Today", "expected_rain_mm": loc["baseline"]["rainfall_mm"], "temp_max": loc["baseline"]["temp_c"] + 2, "temp_min": loc["baseline"]["temp_c"] - 4, "condition": "Seasonal Norm"},
            {"day": "Tomorrow", "expected_rain_mm": round(loc["baseline"]["rainfall_mm"] * 1.1, 1), "temp_max": loc["baseline"]["temp_c"] + 3, "temp_min": loc["baseline"]["temp_c"] - 3, "condition": "Seasonal Norm"},
            {"day": "Day 3", "expected_rain_mm": round(loc["baseline"]["rainfall_mm"] * 0.9, 1), "temp_max": loc["baseline"]["temp_c"] + 1, "temp_min": loc["baseline"]["temp_c"] - 5, "condition": "Seasonal Norm"}
        ],
        "is_live": False,
        "data_source": "Calibrated Regional Baseline (Offline Mode)",
        "source_notes": "Using verified Punjab historical seasonal norms. Open-Meteo external API disconnected or timed out."
    }

    # Query Open-Meteo Free Weather API
    api_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,soil_moisture_0_to_1cm",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,weather_code",
        "timezone": "auto",
        "forecast_days": 3
    }

    try:
        response = requests.get(api_url, params=params, timeout=timeout_seconds)
        if response.status_code == 200:
            payload = response.json()
            current = payload.get("current", {})
            hourly = payload.get("hourly", {})
            daily = payload.get("daily", {})

            live_temp = current.get("temperature_2m")
            live_humidity = current.get("relative_humidity_2m")
            live_precip = current.get("precipitation", 0.0)
            weather_code = current.get("weather_code", 2)

            # 24-hour rainfall accumulation from hourly data
            hourly_precip = hourly.get("precipitation", [])
            rainfall_24h = sum(hourly_precip[:24]) if hourly_precip else float(live_precip)
            hourly_rain_series = [round(float(p or 0.0), 2) for p in hourly_precip[:24]] if hourly_precip else result["hourly_rainfall_24h"]

            # Hourly time labels
            hourly_time_raw = hourly.get("time", [])
            hourly_labels = [t.split("T")[-1][:5] for t in hourly_time_raw[:24]] if hourly_time_raw else result["hourly_time_labels"]

            # Soil moisture
            soil_series = hourly.get("soil_moisture_0_to_1cm", [])
            if soil_series and soil_series[0] is not None:
                soil_moisture = round(float(soil_series[0]) * 100.0, 1)
            else:
                soil_moisture = loc["baseline"]["soil_moisture_pct"]

            # Calibrate river stage to local baseline + local runoff influence
            river_stage = loc["normal_river_level_m"] + min(2.5, rainfall_24h * 0.035)

            # Multi-day forecast formatting
            daily_forecast = []
            daily_times = daily.get("time", [])
            daily_precip = daily.get("precipitation_sum", [])
            daily_max = daily.get("temperature_2m_max", [])
            daily_min = daily.get("temperature_2m_min", [])
            daily_wcode = daily.get("weather_code", [])

            for i in range(min(3, len(daily_times))):
                day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else daily_times[i])
                daily_forecast.append({
                    "day": day_label,
                    "expected_rain_mm": round(float(daily_precip[i] or 0.0), 1) if i < len(daily_precip) else 0.0,
                    "temp_max": round(float(daily_max[i] or 30.0), 1) if i < len(daily_max) else 30.0,
                    "temp_min": round(float(daily_min[i] or 20.0), 1) if i < len(daily_min) else 20.0,
                    "condition": get_weather_desc(daily_wcode[i]) if i < len(daily_wcode) else "Partly Cloudy"
                })

            result.update({
                "rainfall_mm": round(float(rainfall_24h), 1),
                "temp_c": round(float(live_temp), 1) if live_temp is not None else loc["baseline"]["temp_c"],
                "humidity_pct": round(float(live_humidity), 1) if live_humidity is not None else loc["baseline"]["humidity_pct"],
                "soil_moisture_pct": round(soil_moisture, 1),
                "river_water_level_m": round(river_stage, 2),
                "weather_condition": get_weather_desc(weather_code),
                "weather_code": weather_code,
                "hourly_rainfall_24h": hourly_rain_series,
                "hourly_time_labels": hourly_labels,
                "daily_forecast": daily_forecast,
                "is_live": True,
                "data_source": "Live Open-Meteo API Observation",
                "source_notes": f"Real-time telemetry retrieved via Open-Meteo. Current condition: {get_weather_desc(weather_code)}."
            })

    except Exception as e:
        result["is_live"] = False
        result["data_source"] = "Calibrated Regional Baseline (Offline Mode)"
        result["source_notes"] = f"Using regional historical baseline (Open-Meteo query fallback: {type(e).__name__})."

    return result
