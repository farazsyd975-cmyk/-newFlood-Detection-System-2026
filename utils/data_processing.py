"""
=============================================================================
FLOOD DETECTION SYSTEM - ADVANCED DATA PROCESSING UTILITIES
Location references, Punjab river hydrology, baseline benchmarks & input validation.
=============================================================================
"""

import numpy as np
import pandas as pd

# Canonical list of 7 verified Punjab locations with geographical references
LOCATIONS_DATA = {
    "Jalandhar": {
        "name": "Jalandhar",
        "district": "Jalandhar",
        "latitude": 31.3260,
        "longitude": 75.5762,
        "elevation_m": 228.0,
        "nearest_river": "Kali Bein / Sutlej tributary",
        "distance_to_river_km": 12.0,
        "normal_river_level_m": 2.2,
        "danger_river_level_m": 4.5,
        "base_drainage_capacity_pct": 65.0,
        "historical_avg_monsoon_rain_mm": 68.5,
        "hotspot_description": "Doaba plain central lowlands; urban waterlogging along GT Road and seasonal Kali Bein tributary backwaters.",
        "baseline": {
            "rainfall_mm": 5.2,
            "temp_c": 28.5,
            "humidity_pct": 58.0,
            "river_water_level_m": 2.1,
            "soil_moisture_pct": 36.0,
            "prev_rainfall_7d_mm": 18.0,
            "drainage_capacity_pct": 70.0
        }
    },
    "Phagwara": {
        "name": "Phagwara",
        "district": "Kapurthala",
        "latitude": 31.2240,
        "longitude": 75.7708,
        "elevation_m": 234.0,
        "nearest_river": "East Bein drainage basin",
        "distance_to_river_km": 8.5,
        "normal_river_level_m": 2.0,
        "danger_river_level_m": 4.2,
        "base_drainage_capacity_pct": 55.0,
        "historical_avg_monsoon_rain_mm": 64.0,
        "hotspot_description": "Industrial town with agricultural depressions; vulnerable when East Bein rivulets overflow during heavy downpours.",
        "baseline": {
            "rainfall_mm": 4.8,
            "temp_c": 29.0,
            "humidity_pct": 56.0,
            "river_water_level_m": 1.9,
            "soil_moisture_pct": 34.0,
            "prev_rainfall_7d_mm": 15.0,
            "drainage_capacity_pct": 62.0
        }
    },
    "Amritsar": {
        "name": "Amritsar",
        "district": "Amritsar",
        "latitude": 31.6340,
        "longitude": 74.8723,
        "elevation_m": 234.0,
        "nearest_river": "Ravi River / Sakki Nullah",
        "distance_to_river_km": 15.0,
        "normal_river_level_m": 2.4,
        "danger_river_level_m": 4.8,
        "base_drainage_capacity_pct": 70.0,
        "historical_avg_monsoon_rain_mm": 72.0,
        "hotspot_description": "Border district drained by Sakki Nullah; experiences riverine surge when Ravi River discharges exceed 150,000 cusecs.",
        "baseline": {
            "rainfall_mm": 3.6,
            "temp_c": 27.8,
            "humidity_pct": 52.0,
            "river_water_level_m": 2.2,
            "soil_moisture_pct": 32.0,
            "prev_rainfall_7d_mm": 12.0,
            "drainage_capacity_pct": 75.0
        }
    },
    "Ludhiana": {
        "name": "Ludhiana",
        "district": "Ludhiana",
        "latitude": 30.9010,
        "longitude": 75.8573,
        "elevation_m": 244.0,
        "nearest_river": "Sutlej River & Buddha Nullah",
        "distance_to_river_km": 6.0,
        "normal_river_level_m": 2.6,
        "danger_river_level_m": 5.0,
        "base_drainage_capacity_pct": 45.0,
        "historical_avg_monsoon_rain_mm": 76.0,
        "hotspot_description": "Dense urban industrial hub; chronic hotspot due to Buddha Nullah backflow and Sutlej embankments along Phillaur corridor.",
        "baseline": {
            "rainfall_mm": 6.5,
            "temp_c": 29.5,
            "humidity_pct": 60.0,
            "river_water_level_m": 2.5,
            "soil_moisture_pct": 38.0,
            "prev_rainfall_7d_mm": 22.0,
            "drainage_capacity_pct": 48.0
        }
    },
    "Kapurthala": {
        "name": "Kapurthala",
        "district": "Kapurthala",
        "latitude": 31.3800,
        "longitude": 75.3810,
        "elevation_m": 225.0,
        "nearest_river": "Beas River & Harike Wetland",
        "distance_to_river_km": 7.0,
        "normal_river_level_m": 2.5,
        "danger_river_level_m": 4.4,
        "base_drainage_capacity_pct": 50.0,
        "historical_avg_monsoon_rain_mm": 70.0,
        "hotspot_description": "Low-lying alluvial Mand area near Beas-Sutlej confluence at Harike; highest vulnerability to prolonged water accumulation.",
        "baseline": {
            "rainfall_mm": 5.8,
            "temp_c": 28.0,
            "humidity_pct": 62.0,
            "river_water_level_m": 2.4,
            "soil_moisture_pct": 42.0,
            "prev_rainfall_7d_mm": 20.0,
            "drainage_capacity_pct": 52.0
        }
    },
    "Hoshiarpur": {
        "name": "Hoshiarpur",
        "district": "Hoshiarpur",
        "latitude": 31.5143,
        "longitude": 75.9115,
        "elevation_m": 296.0,
        "nearest_river": "Shivalik Seasonal Torrents (Choes)",
        "distance_to_river_km": 4.0,
        "normal_river_level_m": 1.5,
        "danger_river_level_m": 3.8,
        "base_drainage_capacity_pct": 60.0,
        "historical_avg_monsoon_rain_mm": 88.0,
        "hotspot_description": "Sub-mountainous Shivalik tract traversed by dozens of dry sandy torrents (choes) prone to high-velocity flash runoff.",
        "baseline": {
            "rainfall_mm": 8.0,
            "temp_c": 26.5,
            "humidity_pct": 64.0,
            "river_water_level_m": 1.6,
            "soil_moisture_pct": 40.0,
            "prev_rainfall_7d_mm": 28.0,
            "drainage_capacity_pct": 65.0
        }
    },
    "Nawanshahr": {
        "name": "Nawanshahr",
        "district": "Shaheed Bhagat Singh Nagar",
        "latitude": 31.1240,
        "longitude": 76.1160,
        "elevation_m": 250.0,
        "nearest_river": "Sutlej River floodplain",
        "distance_to_river_km": 5.5,
        "normal_river_level_m": 2.3,
        "danger_river_level_m": 4.7,
        "base_drainage_capacity_pct": 58.0,
        "historical_avg_monsoon_rain_mm": 74.0,
        "hotspot_description": "Directly bounded by Sutlej dykes downriver of Ropar Barrage; highly susceptible to river breaches when Bhakra discharges surge.",
        "baseline": {
            "rainfall_mm": 6.0,
            "temp_c": 28.2,
            "humidity_pct": 59.0,
            "river_water_level_m": 2.2,
            "soil_moisture_pct": 37.0,
            "prev_rainfall_7d_mm": 21.0,
            "drainage_capacity_pct": 60.0
        }
    }
}

FEATURE_COLUMNS = [
    "rainfall_mm",
    "temp_c",
    "humidity_pct",
    "river_water_level_m",
    "soil_moisture_pct",
    "prev_rainfall_7d_mm",
    "elevation_m",
    "distance_to_river_km",
    "drainage_capacity_pct"
]

RISK_METADATA = {
    0: {
        "label": "Low",
        "color": "#16a34a",
        "badge_class": "risk-low",
        "summary": "Normal Hydrological Conditions",
        "advisory": "Water levels are safe and well within natural drainage capacity. Standard routine observation is sufficient.",
        "action": "Routine observation."
    },
    1: {
        "label": "Moderate",
        "color": "#ca8a04",
        "badge_class": "risk-moderate",
        "summary": "Elevated Hydrological Risk / Local Waterlogging",
        "advisory": "Localized surface water accumulation expected in low-lying agricultural depressions and municipal bottlenecks.",
        "action": "Inspect municipal drains, clear culvert debris, and alert standby pump crews."
    },
    2: {
        "label": "High",
        "color": "#ea580c",
        "badge_class": "risk-high",
        "summary": "High Flood Hazard Warning",
        "advisory": "River water level approaching warning stage or intense overland saturation. Substantial inundation risk along embankments.",
        "action": "Issue flood warning to riverside residents; reinforce weak bunds; prepare emergency evacuation centers."
    },
    3: {
        "label": "Severe",
        "color": "#dc2626",
        "badge_class": "risk-severe",
        "summary": "Critical Inundation / Embankment Breach Danger",
        "advisory": "Danger stage exceeded with saturated catchment. Imminent or active flooding threatening populated areas.",
        "action": "Trigger immediate emergency evacuation in floodplain sectors; deploy NDRF/SDRF rescue boats and de-watering equipment."
    }
}

CAUSE_METADATA = {
    0: {
        "label": "None / Normal Drainage",
        "title": "Normal Hydrological Balance",
        "color": "#16a34a",
        "badge_class": "cause-safe",
        "explanation": "Atmospheric precipitation and river discharge are well within natural absorption and conveyance capacities.",
        "driver_keys": ["rainfall_mm", "river_water_level_m", "drainage_capacity_pct"]
    },
    1: {
        "label": "Rainfall-Driven Flooding",
        "title": "Intense Precipitation Inundation",
        "color": "#0284c7",
        "badge_class": "cause-rainfall",
        "explanation": "High-intensity rainfall exceeds the surface soil infiltration capacity, causing rapid overland runoff even while rivers remain below danger levels.",
        "driver_keys": ["rainfall_mm", "prev_rainfall_7d_mm", "soil_moisture_pct"]
    },
    2: {
        "label": "Drainage-Driven Flooding",
        "title": "Urban Storm Drainage Congestion",
        "color": "#ca8a04",
        "badge_class": "cause-drainage",
        "explanation": "Moderate to heavy rainfall cannot discharge due to restricted culverts, clogged storm channels (such as Buddha Nullah), or low municipal gradient.",
        "driver_keys": ["drainage_capacity_pct", "rainfall_mm", "elevation_m"]
    },
    3: {
        "label": "River Overflow",
        "title": "Riverine Surge & Barrage Discharge",
        "color": "#ea580c",
        "badge_class": "cause-river",
        "explanation": "River water stage approaches or exceeds danger mark primarily due to upstream dam releases (e.g., Bhakra/Pong) and catchment inflows rather than local rainfall.",
        "driver_keys": ["river_water_level_m", "distance_to_river_km", "danger_river_level_m"]
    },
    4: {
        "label": "Combined Flood Risk",
        "title": "Compound Multi-Factor Catastrophe",
        "color": "#dc2626",
        "badge_class": "cause-combined",
        "explanation": "Confluence of extreme precipitation, saturated soil, choked drainage, and swollen river stage simultaneously, similar to the historical July 2023 disaster.",
        "driver_keys": ["rainfall_mm", "river_water_level_m", "soil_moisture_pct", "drainage_capacity_pct"]
    }
}

# Historical Punjab Monsoon Benchmarks (2018 - 2024 Records)
PUNJAB_HISTORICAL_DATA = {
    "annual_monsoon_records": [
        {"year": 2018, "monsoon_rain_mm": 492.0, "flood_events": 2, "major_affected": "Ropar, Nawanshahr"},
        {"year": 2019, "monsoon_rain_mm": 548.5, "flood_events": 5, "major_affected": "Jalandhar, Kapurthala, Ludhiana (Sutlej breach)"},
        {"year": 2020, "monsoon_rain_mm": 415.2, "flood_events": 1, "major_affected": "Localized urban waterlogging"},
        {"year": 2021, "monsoon_rain_mm": 438.0, "flood_events": 1, "major_affected": "Ghaggar basin"},
        {"year": 2022, "monsoon_rain_mm": 462.4, "flood_events": 2, "major_affected": "Hoshiarpur choes, Fazilka"},
        {"year": 2023, "monsoon_rain_mm": 678.0, "flood_events": 8, "major_affected": "Statewide disaster: Sutlej, Beas, Ghaggar (Historic flood)"},
        {"year": 2024, "monsoon_rain_mm": 485.0, "flood_events": 2, "major_affected": "Gurdaspur, Hoshiarpur foothill torrents"}
    ],
    "monthly_averages_punjab": [
        {"month": "May", "avg_rain_mm": 18.2, "historical_risk": "Low"},
        {"month": "Jun", "avg_rain_mm": 52.4, "historical_risk": "Low to Moderate"},
        {"month": "Jul", "avg_rain_mm": 182.6, "historical_risk": "High (Peak Monsoon)"},
        {"month": "Aug", "avg_rain_mm": 164.2, "historical_risk": "High (Saturated Ground)"},
        {"month": "Sep", "avg_rain_mm": 78.5, "historical_risk": "Moderate (Receding Monsoon)"},
        {"month": "Oct", "avg_rain_mm": 12.0, "historical_risk": "Low (Dry Autumn)"}
    ]
}


def sanitize_input_features(raw_data, location_name="Jalandhar"):
    """
    Validate, sanitize, and impute missing environmental parameters.
    """
    loc_meta = LOCATIONS_DATA.get(location_name, LOCATIONS_DATA["Jalandhar"])

    def _clean_val(key, default_val, min_val, max_val):
        val = raw_data.get(key)
        if val is None or val == "":
            val = default_val
        try:
            val = float(val)
        except (ValueError, TypeError):
            val = float(default_val)
        return float(np.clip(val, min_val, max_val))

    rainfall = _clean_val("rainfall_mm", loc_meta["baseline"]["rainfall_mm"], 0.0, 500.0)
    temp = _clean_val("temp_c", loc_meta["baseline"]["temp_c"], 0.0, 55.0)
    humidity = _clean_val("humidity_pct", loc_meta["baseline"]["humidity_pct"], 10.0, 100.0)
    river_level = _clean_val("river_water_level_m", loc_meta["baseline"]["river_water_level_m"], 0.0, 15.0)
    soil_moisture = _clean_val("soil_moisture_pct", loc_meta["baseline"]["soil_moisture_pct"], 5.0, 100.0)
    prev_rain = _clean_val("prev_rainfall_7d_mm", loc_meta["baseline"]["prev_rainfall_7d_mm"], 0.0, 800.0)
    elevation = _clean_val("elevation_m", loc_meta["elevation_m"], 100.0, 800.0)
    distance = _clean_val("distance_to_river_km", loc_meta["distance_to_river_km"], 0.1, 100.0)
    drainage = _clean_val("drainage_capacity_pct", loc_meta["baseline"].get("drainage_capacity_pct", 65.0), 5.0, 100.0)

    clean_dict = {
        "rainfall_mm": round(rainfall, 2),
        "temp_c": round(temp, 1),
        "humidity_pct": round(humidity, 1),
        "river_water_level_m": round(river_level, 2),
        "soil_moisture_pct": round(soil_moisture, 1),
        "prev_rainfall_7d_mm": round(prev_rain, 2),
        "elevation_m": round(elevation, 1),
        "distance_to_river_km": round(distance, 1),
        "drainage_capacity_pct": round(drainage, 1)
    }

    return clean_dict


def features_to_dataframe(features_dict):
    """Convert cleaned feature dictionary to single-row DataFrame."""
    return pd.DataFrame([features_dict], columns=FEATURE_COLUMNS)
