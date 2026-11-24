"""
=============================================================================
FLOOD DETECTION SYSTEM - ADVANCED ML TRAINING PIPELINE
Dual-Engine: Multi-Class Flood Risk & Cause-Aware Classification
Calibrated on Historical Punjab Hydrological Basins (CWC & IMD Thresholds)
=============================================================================
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# ---------------------------------------------------------------------------
# 1. Location Reference Catalog (Actual Punjab Coordinates & Hydrology)
# ---------------------------------------------------------------------------
LOCATIONS = {
    "Jalandhar": {
        "lat": 31.3260,
        "lon": 75.5762,
        "elevation_m": 228.0,
        "nearest_river": "Kali Bein / Sutlej tributary",
        "avg_river_dist_km": 12.0,
        "normal_river_level_m": 2.2,
        "danger_river_level_m": 4.5,
        "base_drainage_capacity_pct": 65.0
    },
    "Phagwara": {
        "lat": 31.2240,
        "lon": 75.7708,
        "elevation_m": 234.0,
        "nearest_river": "East Bein drainage basin",
        "avg_river_dist_km": 8.5,
        "normal_river_level_m": 2.0,
        "danger_river_level_m": 4.2,
        "base_drainage_capacity_pct": 55.0
    },
    "Amritsar": {
        "lat": 31.6340,
        "lon": 74.8723,
        "elevation_m": 234.0,
        "nearest_river": "Ravi River / Sakki Nullah",
        "avg_river_dist_km": 15.0,
        "normal_river_level_m": 2.4,
        "danger_river_level_m": 4.8,
        "base_drainage_capacity_pct": 70.0
    },
    "Ludhiana": {
        "lat": 30.9010,
        "lon": 75.8573,
        "elevation_m": 244.0,
        "nearest_river": "Sutlej River & Buddha Nullah",
        "avg_river_dist_km": 6.0,
        "normal_river_level_m": 2.6,
        "danger_river_level_m": 5.0,
        "base_drainage_capacity_pct": 45.0  # Urban industrial drainage bottleneck (Buddha Nullah)
    },
    "Kapurthala": {
        "lat": 31.3800,
        "lon": 75.3810,
        "elevation_m": 225.0,
        "nearest_river": "Beas River & Harike Wetland",
        "avg_river_dist_km": 7.0,
        "normal_river_level_m": 2.5,
        "danger_river_level_m": 4.4,
        "base_drainage_capacity_pct": 50.0  # Low-lying confluence Mand area
    },
    "Hoshiarpur": {
        "lat": 31.5143,
        "lon": 75.9115,
        "elevation_m": 296.0,
        "nearest_river": "Shivalik Seasonal Torrents (Choes)",
        "avg_river_dist_km": 4.0,
        "normal_river_level_m": 1.5,
        "danger_river_level_m": 3.8,
        "base_drainage_capacity_pct": 60.0
    },
    "Nawanshahr": {
        "lat": 31.1240,
        "lon": 76.1160,
        "elevation_m": 250.0,
        "nearest_river": "Sutlej River floodplain",
        "avg_river_dist_km": 5.5,
        "normal_river_level_m": 2.3,
        "danger_river_level_m": 4.7,
        "base_drainage_capacity_pct": 58.0
    }
}

FEATURES = [
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

RISK_LABELS = {
    0: "Low",
    1: "Moderate",
    2: "High",
    3: "Severe"
}

CAUSE_LABELS = {
    0: "None / Normal Drainage",
    1: "Rainfall-Driven Flooding",
    2: "Drainage-Driven Flooding",
    3: "River Overflow",
    4: "Combined Flood Risk"
}


def generate_advanced_dataset(num_samples=2100, random_seed=42):
    """
    Synthesize an environmental dataset calibrated on realistic Punjab monsoon ranges,
    incorporating drainage capacity and cause-aware hydrological ground truths.
    """
    np.random.seed(random_seed)
    data = []
    city_names = list(LOCATIONS.keys())
    samples_per_city = num_samples // len(city_names)

    for city in city_names:
        info = LOCATIONS[city]
        base_elev = info["elevation_m"]
        base_dist = info["avg_river_dist_km"]
        norm_river = info["normal_river_level_m"]
        dang_river = info["danger_river_level_m"]
        base_drainage = info["base_drainage_capacity_pct"]

        for _ in range(samples_per_city):
            # Scenario types:
            # 0: Normal / Dry weather (38%)
            # 1: Rainfall-dominant monsoon downpour (22%)
            # 2: Drainage-choked urban flash accumulation (16%)
            # 3: Upstream river reservoir release / river surge (12%)
            # 4: Catastrophic combined monsoon event (e.g., July 2023) (12%)
            scenario = np.random.choice([0, 1, 2, 3, 4], p=[0.38, 0.22, 0.16, 0.12, 0.12])

            if scenario == 0:
                # Normal / Dry conditions
                rainfall = np.random.exponential(scale=5.0)
                rainfall = min(rainfall, 25.0)
                temp = np.random.uniform(18.0, 39.0)
                humidity = np.random.uniform(28.0, 65.0)
                prev_rain = np.random.exponential(scale=10.0)
                soil_moisture = np.random.uniform(15.0, 45.0)
                river_level = np.random.normal(norm_river, 0.25)
                river_level = max(0.5, min(river_level, norm_river + 0.5))
                drainage = np.random.uniform(base_drainage, 95.0)
                cause_code = 0

            elif scenario == 1:
                # Rainfall-dominant (Torrential local cloudburst, river normal, drainage moderate)
                rainfall = np.random.uniform(75.0, 160.0)
                temp = np.random.uniform(24.0, 32.0)
                humidity = np.random.uniform(78.0, 96.0)
                prev_rain = np.random.uniform(40.0, 140.0)
                soil_moisture = np.random.uniform(70.0, 92.0)
                river_level = np.random.uniform(norm_river + 0.2, dang_river - 0.3)
                drainage = np.random.uniform(50.0, 85.0)
                cause_code = 1  # Rainfall-Driven

            elif scenario == 2:
                # Drainage-driven (Moderate rain, but storm channels choked/backed up)
                rainfall = np.random.uniform(35.0, 75.0)
                temp = np.random.uniform(25.0, 33.0)
                humidity = np.random.uniform(65.0, 88.0)
                prev_rain = np.random.uniform(25.0, 80.0)
                soil_moisture = np.random.uniform(55.0, 78.0)
                river_level = np.random.uniform(norm_river, dang_river - 0.5)
                drainage = np.random.uniform(15.0, 42.0)  # Severely congested drainage
                cause_code = 2  # Drainage-Driven

            elif scenario == 3:
                # River overflow (Upstream dam release from Bhakra/Pong into Sutlej/Beas)
                rainfall = np.random.uniform(5.0, 45.0)  # Local rain may be low!
                temp = np.random.uniform(24.0, 31.0)
                humidity = np.random.uniform(60.0, 85.0)
                prev_rain = np.random.uniform(15.0, 60.0)
                soil_moisture = np.random.uniform(45.0, 75.0)
                river_level = np.random.uniform(dang_river - 0.1, dang_river + 1.8)
                drainage = np.random.uniform(45.0, 80.0)
                cause_code = 3  # River Overflow

            else:
                # Catastrophic combined monsoon flood (July 2023 flood archetype)
                rainfall = np.random.uniform(110.0, 240.0)
                temp = np.random.uniform(23.0, 29.0)
                humidity = np.random.uniform(85.0, 99.0)
                prev_rain = np.random.uniform(140.0, 320.0)
                soil_moisture = np.random.uniform(85.0, 99.0)
                river_level = np.random.uniform(dang_river + 0.2, dang_river + 2.5)
                drainage = np.random.uniform(10.0, 40.0)  # Severe choking & inundation
                cause_code = 4  # Combined Flood Risk

            elevation = base_elev + np.random.uniform(-1.5, 1.5)
            distance_river = max(1.0, base_dist + np.random.uniform(-1.0, 1.0))

            # Hydrological Runoff & Vulnerability Physics Index
            # Infiltration excess runoff potential
            runoff_potential = rainfall * (soil_moisture / 100.0)
            antecedent_impact = prev_rain * 0.20

            # Drainage congestion backlog: water retained when drainage capacity is choked
            drainage_backlog = (rainfall * ((100.0 - drainage) / 100.0) * 0.8) + ((100.0 - drainage) * 0.25)

            # River pressure relative to danger mark
            river_ratio = river_level / dang_river
            river_pressure = max(0.0, (river_ratio - 0.70) * 65.0)

            # Topographical modifier
            elevation_modifier = (300.0 - elevation) * 0.08
            proximity_modifier = (20.0 - min(distance_river, 20.0)) * 0.75
            topography_factor = elevation_modifier + proximity_modifier

            composite_score = (
                0.28 * runoff_potential +
                0.22 * drainage_backlog +
                0.25 * river_pressure +
                0.15 * antecedent_impact +
                0.10 * topography_factor
            )

            # Add stochastic natural sensor variance
            composite_score += np.random.normal(0, 2.5)

            # Multi-class Risk Thresholds calibrated for Punjab basins
            if composite_score < 24.0:
                risk_class = 0  # Low
                cause_code = 0  # Normal Drainage / Safe
            elif composite_score < 48.0:
                risk_class = 1  # Moderate
                if cause_code == 0:
                    cause_code = 2 if drainage < 50.0 else 1
            elif composite_score < 74.0:
                risk_class = 2  # High
                if cause_code == 0:
                    cause_code = 3 if river_level >= (dang_river - 0.3) else 1
            else:
                risk_class = 3  # Severe
                if cause_code == 0:
                    cause_code = 4  # Combined

            data.append({
                "location": city,
                "latitude": info["lat"],
                "longitude": info["lon"],
                "rainfall_mm": round(rainfall, 2),
                "temp_c": round(temp, 1),
                "humidity_pct": round(humidity, 1),
                "river_water_level_m": round(river_level, 2),
                "soil_moisture_pct": round(soil_moisture, 1),
                "prev_rainfall_7d_mm": round(prev_rain, 2),
                "elevation_m": round(elevation, 1),
                "distance_to_river_km": round(distance_river, 1),
                "drainage_capacity_pct": round(drainage, 1),
                "composite_risk_score": round(composite_score, 2),
                "flood_risk": risk_class,
                "flood_risk_label": RISK_LABELS[risk_class],
                "probable_cause_code": cause_code,
                "probable_cause_label": CAUSE_LABELS[cause_code]
            })

    df = pd.DataFrame(data)
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df


def train_and_evaluate(df, output_dir):
    """
    Train both Flood Risk and Cause-Aware Classifier pipelines, evaluate,
    and persist artifacts.
    """
    os.makedirs(output_dir, exist_ok=True)
    dataset_dir = os.path.join(output_dir, "..", "dataset")
    os.makedirs(dataset_dir, exist_ok=True)

    # Save dataset CSV
    csv_path = os.path.join(dataset_dir, "flood_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"[Dataset] Saved {len(df)} records to: {csv_path}")

    X = df[FEATURES]
    y_risk = df["flood_risk"]
    y_cause = df["probable_cause_code"]

    # Stratified Train/Test Split (80/20)
    X_train, X_test, y_risk_train, y_risk_test, y_cause_train, y_cause_test = train_test_split(
        X, y_risk, y_cause, test_size=0.20, random_state=42, stratify=y_risk
    )

    print(f"[Split] Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # -----------------------------------------------------------------------
    # 1. Primary Model: Random Forest Risk Pipeline
    # -----------------------------------------------------------------------
    rf_risk_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=130,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1
        ))
    ])

    # Baseline: Decision Tree Classifier
    dt_baseline = DecisionTreeClassifier(max_depth=6, min_samples_split=8, random_state=42)
    dt_baseline.fit(X_train, y_risk_train)
    dt_acc = accuracy_score(y_risk_test, dt_baseline.predict(X_test))

    # Cross-validation
    cv_scores = cross_val_score(rf_risk_pipeline, X_train, y_risk_train, cv=5, scoring="accuracy")
    rf_risk_pipeline.fit(X_train, y_risk_train)

    y_pred_risk = rf_risk_pipeline.predict(X_test)
    risk_acc = accuracy_score(y_risk_test, y_pred_risk)
    precision_macro = precision_score(y_risk_test, y_pred_risk, average="macro", zero_division=0)
    precision_weighted = precision_score(y_risk_test, y_pred_risk, average="weighted", zero_division=0)
    recall_macro = recall_score(y_risk_test, y_pred_risk, average="macro", zero_division=0)
    recall_weighted = recall_score(y_risk_test, y_pred_risk, average="weighted", zero_division=0)
    f1_macro = f1_score(y_risk_test, y_pred_risk, average="macro", zero_division=0)
    f1_weighted = f1_score(y_risk_test, y_pred_risk, average="weighted", zero_division=0)

    cm_risk = confusion_matrix(y_risk_test, y_pred_risk).tolist()
    class_report_risk = classification_report(
        y_risk_test, y_pred_risk, target_names=["Low", "Moderate", "High", "Severe"], output_dict=True
    )

    rf_estimator = rf_risk_pipeline.named_steps["rf"]
    feature_importances = {
        feat: round(float(imp), 4)
        for feat, imp in zip(FEATURES, rf_estimator.feature_importances_)
    }
    sorted_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

    # -----------------------------------------------------------------------
    # 2. Secondary Model: Cause-Aware Classifier Pipeline
    # -----------------------------------------------------------------------
    rf_cause_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        ))
    ])
    rf_cause_pipeline.fit(X_train, y_cause_train)
    y_pred_cause = rf_cause_pipeline.predict(X_test)
    cause_acc = accuracy_score(y_cause_test, y_pred_cause)

    print("\n" + "=" * 60)
    print("FLOOD RISK RANDOM FOREST EVALUATION (TEST SET)")
    print("=" * 60)
    print(f"Risk Test Accuracy:   {risk_acc * 100:.2f}% (Baseline DT: {dt_acc * 100:.2f}%)")
    print(f"5-Fold CV Accuracy:   {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")
    print(f"Cause Accuracy:       {cause_acc * 100:.2f}%")
    print(f"Weighted F1-Score:    {f1_weighted * 100:.2f}%")
    print(f"Macro F1-Score:       {f1_macro * 100:.2f}%")
    print("\nFeature Importances:")
    for feat, imp in sorted_importances.items():
        print(f"  - {feat:24s}: {imp * 100:.2f}%")
    print("=" * 60)

    # Persist Models
    model_path = os.path.join(output_dir, "flood_model.pkl")
    cause_model_path = os.path.join(output_dir, "cause_model.pkl")
    joblib.dump(rf_risk_pipeline, model_path)
    joblib.dump(rf_cause_pipeline, cause_model_path)
    print(f"[Model Artifacts] Saved risk model to: {model_path}")
    print(f"[Model Artifacts] Saved cause model to: {cause_model_path}")

    # Metadata
    metadata = {
        "model_type": "Random Forest Classifier (130 Trees with StandardScaler)",
        "baseline_model": "Decision Tree Classifier",
        "cause_model_type": "Random Forest Cause-Aware Classifier (100 Trees)",
        "dataset_total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features": FEATURES,
        "classes": RISK_LABELS,
        "cause_classes": CAUSE_LABELS,
        "metrics": {
            "accuracy": round(risk_acc, 4),
            "precision_macro": round(precision_macro, 4),
            "precision_weighted": round(precision_weighted, 4),
            "recall_macro": round(recall_macro, 4),
            "recall_weighted": round(recall_weighted, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
            "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
            "cv_accuracy_std": round(float(cv_scores.std()), 4),
            "decision_tree_accuracy": round(dt_acc, 4),
            "cause_accuracy": round(cause_acc, 4)
        },
        "confusion_matrix": cm_risk,
        "feature_importances": sorted_importances,
        "classification_report": class_report_risk,
        "locations": LOCATIONS
    }

    metadata_path = os.path.join(output_dir, "model_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Metadata] Evaluation report saved to: {metadata_path}")

    return rf_risk_pipeline, rf_cause_pipeline, metadata


if __name__ == "__main__":
    print("Initializing Advanced Punjab Flood Detection & Cause-Aware Training...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base_dir, "model")

    df = generate_advanced_dataset(num_samples=2100, random_seed=42)
    train_and_evaluate(df, model_dir)
    print("\nAdvanced Training completed successfully!")
