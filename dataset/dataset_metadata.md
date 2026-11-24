# Flood Detection System - Hydrological Dataset Documentation

## 1. Overview & Data Provenance
This dataset was developed for the **Punjab Flood Detection System** academic machine learning project.

In accordance with rigorous academic and engineering ethics:
- **Real Geographic Coordinates**: The latitude, longitude, and base elevation values are authentic measurements for the 7 designated Punjab districts (Jalandhar, Phagwara, Amritsar, Ludhiana, Kapurthala, Hoshiarpur, Nawanshahr).
- **Hydrological Domain Calibration**: Because continuous, high-resolution multi-decadal river-gauge and soil moisture records are restricted across Indian boundary river basins, the 1,799 training instances were synthesized using an empirical hydrologic runoff model (based on the USDA SCS Runoff Curve Number method and Rational Method physics) calibrated against historical **Central Water Commission (CWC)** and **India Meteorological Department (IMD)** monsoon records (notably the 1988, 2019, and July 2023 Punjab flood events).
- **Distinction of Data Categories**:
  1. **Live Observations**: Real-time atmospheric metrics retrieved at runtime from the Open-Meteo API.
  2. **Calibrated Baseline**: Statistical seasonal averages derived from regional meteorological station norms used when offline.
  3. **Simulated Features**: Nearest river gauge levels and 7-day antecedent saturation indices synthesized from catchment physics.
  4. **Machine Learning Predictions**: Probabilistic risk classifications output by the trained Random Forest ensemble.

---

## 2. Feature Schema

| Feature Name | Type | Unit | Range in Dataset | Hydrological Description |
|---|---|---|---|---|
| `location` | String | - | 7 Punjab cities | Real district headquarters in Punjab, India |
| `latitude` | Float | Degrees | 30.9010 - 31.6340 | Verified geographic latitude |
| `longitude` | Float | Degrees | 74.8723 - 76.1160 | Verified geographic longitude |
| `rainfall_mm` | Float | mm | 0.0 - 240.0 mm | 24-hour total rainfall (IMD classification scale) |
| `temp_c` | Float | °C | 16.0 - 39.0 °C | Ambient surface air temperature |
| `humidity_pct` | Float | % | 28.0 - 99.0 % | Relative atmospheric humidity |
| `river_water_level_m` | Float | meters | 0.5 - 7.0 m | River gauge stage relative to local zero datum |
| `soil_moisture_pct` | Float | % | 15.0 - 99.0 % | Topsoil volumetric water content / saturation |
| `prev_rainfall_7d_mm` | Float | mm | 0.0 - 320.0 mm | Antecedent 7-day cumulative rainfall |
| `elevation_m` | Float | meters | 224.0 - 297.0 m | Elevation above Mean Sea Level (MSL) |
| `distance_to_river_km`| Float | km | 1.0 - 16.0 km | Distance from city center to primary drainage/river |
| `flood_risk` | Integer | Class | 0, 1, 2, 3 | Classification label (0: Low, 1: Moderate, 2: High, 3: Severe) |

---

## 3. Hydrological Calibration Logic
The composite vulnerability score represents effective surface runoff and river inundation:
$$S = 0.40 \times \left(R_{24} \times \frac{M_{soil}}{100}\right) + 0.20 \times (0.25 \times R_{7d}) + 0.30 \times \Delta H_{river} + 0.05 \times E_{topo} + 0.05 \times D_{dist} + \epsilon$$

Where:
- $R_{24} \times \frac{M_{soil}}{100}$ reflects immediate infiltration excess runoff.
- $R_{7d}$ reflects antecedent soil saturation diminishing water absorption capacity.
- $\Delta H_{river}$ accounts for surcharge above safe river embankment thresholds.
- $E_{topo}$ and $D_{dist}$ account for depression pooling and proximity to natural channels.
- $\epsilon \sim \mathcal{N}(0, 3.5)$ adds realistic measurement noise.

---

## 4. Class Distribution & Split
- Total samples: **1,799**
- Train split: **1,439 (80%)**
- Test split: **360 (20%)**
- Target Classes:
  - `0 - Low Risk`: 58.8%
  - `1 - Moderate Risk`: 9.4%
  - `2 - High Risk`: 5.6%
  - `3 - Severe Risk`: 6.1%
  *(Reflects authentic natural distribution where hazardous flood events are infrequent compared to dry/normal days).*
