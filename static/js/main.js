/**
 * ==============================================================================
 * FLOOD DETECTION SYSTEM - ADVANCED FRONTEND CONTROLLER
 * Coordinates live telemetry, cause-aware ML inference, XAI, and simulation.
 * ==============================================================================
 */

document.addEventListener("DOMContentLoaded", function () {
    // DOM Element References
    const locationSelect = document.getElementById("location-select");
    const stationBadge = document.getElementById("station-badge");
    const geoRiver = document.getElementById("geo-river");
    const geoCoords = document.getElementById("geo-coords");
    const geoDangerStage = document.getElementById("geo-danger-stage");
    const geoHotspotDesc = document.getElementById("geo-hotspot-desc");
    const globalDataSource = document.getElementById("global-data-source");
    const weatherCondition = document.getElementById("weather-condition");
    const historicalAnomalyBadge = document.getElementById("historical-anomaly-badge");

    const btnFetchLive = document.getElementById("btn-fetch-live");
    const toggleSimBtn = document.getElementById("toggle-sim-mode");
    const simPresetsPanel = document.getElementById("sim-presets-panel");
    const predictionForm = document.getElementById("prediction-form");
    const btnPredict = document.getElementById("btn-predict");
    const linkResponsePlan = document.getElementById("link-response-plan");

    // Environmental Parameter Inputs & Badges
    const inputs = {
        rainfall: document.getElementById("input-rainfall"),
        riverLevel: document.getElementById("input-river-level"),
        soilMoisture: document.getElementById("input-soil-moisture"),
        drainage: document.getElementById("input-drainage"),
        prevRain: document.getElementById("input-prev-rain"),
        temp: document.getElementById("input-temp"),
        humidity: document.getElementById("input-humidity"),
        elevation: document.getElementById("input-elevation"),
        distance: document.getElementById("input-distance"),
        dataSource: document.getElementById("input-data-source")
    };

    const badges = {
        rainfall: document.getElementById("val-rainfall"),
        riverLevel: document.getElementById("val-river-level"),
        soilMoisture: document.getElementById("val-soil-moisture"),
        drainage: document.getElementById("val-drainage"),
        prevRain: document.getElementById("val-prev-rain"),
        temp: document.getElementById("val-temp"),
        humidity: document.getElementById("val-humidity")
    };

    // Result DOM Elements
    const resultBox = document.querySelector(".result-box");
    const resultRiskLabel = document.getElementById("result-risk-label");
    const resultConfidenceBadge = document.getElementById("result-confidence-badge");
    const resultSummary = document.getElementById("result-summary");
    const resultAdvisory = document.getElementById("result-advisory");
    const resultAction = document.getElementById("result-action");
    const resultTimestamp = document.getElementById("result-timestamp");
    const compositeScoreVal = document.getElementById("composite-score-val");
    const compositeScoreFill = document.getElementById("composite-score-fill");

    // Cause-Aware DOM Elements
    const causeBanner = document.getElementById("cause-banner");
    const causeTitle = document.getElementById("cause-title");
    const causeConfBadge = document.getElementById("cause-conf-badge");
    const causeExplanation = document.getElementById("cause-explanation");
    const causeEvidenceList = document.getElementById("cause-evidence-list");

    // Weather & Forecast Elements
    const forecastCardsContainer = document.getElementById("forecast-cards-container");
    const forecastLiveIndicator = document.getElementById("forecast-live-indicator");
    const hourlyStationName = document.getElementById("hourly-station-name");
    let hourlyRainChart = null;

    // What-If & Comparison Elements
    const whatifOutcomeCard = document.getElementById("whatif-outcome-card");
    const btnCompareStations = document.getElementById("btn-compare-stations");
    const comparisonModal = document.getElementById("comparison-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const comparisonTableBody = document.getElementById("comparison-table-body");
    let comparisonChartInstance = null;

    // Emergency Alert Banner
    const emergencyAlertBanner = document.getElementById("emergency-alert-banner");
    const emergencyBannerText = document.getElementById("emergency-banner-text");
    const btnDismissAlertBanner = document.getElementById("btn-dismiss-alert-banner");

    // XAI List Container
    const xaiElevatingList = document.getElementById("xai-elevating-list");

    // Probability Bars
    const probBars = {
        Low: document.getElementById("bar-prob-low"),
        Moderate: document.getElementById("bar-prob-mod"),
        High: document.getElementById("bar-prob-high"),
        Severe: document.getElementById("bar-prob-sev")
    };

    const probTexts = {
        Low: document.getElementById("txt-prob-low"),
        Moderate: document.getElementById("txt-prob-mod"),
        High: document.getElementById("txt-prob-high"),
        Severe: document.getElementById("txt-prob-sev")
    };

    let isSimulationMode = false;

    // -----------------------------------------------------------------------
    // 1. Station Selection Handlers
    // -----------------------------------------------------------------------

    function selectStation(cityName, refreshWeather = true) {
        if (!cityName) return;

        if (locationSelect && locationSelect.value !== cityName) {
            locationSelect.value = cityName;
        }

        document.querySelectorAll(".station-pill").forEach(pill => {
            if (pill.getAttribute("data-city") === cityName) {
                pill.classList.add("active");
            } else {
                pill.classList.remove("active");
            }
        });

        if (typeof centerMapOnStation === "function") {
            centerMapOnStation(cityName);
        }

        if (linkResponsePlan) {
            linkResponsePlan.href = `/response-planning?city=${encodeURIComponent(cityName)}`;
            linkResponsePlan.textContent = `🛡️ View Full Response & Priority Plan for ${cityName} ➔`;
        }

        if (refreshWeather) {
            loadStationTelemetry(cityName);
        }
    }

    if (locationSelect) {
        locationSelect.addEventListener("change", function () {
            selectStation(this.value, true);
        });
    }

    document.querySelectorAll(".station-pill").forEach(pill => {
        pill.addEventListener("click", function () {
            const city = this.getAttribute("data-city");
            selectStation(city, true);
        });
    });

    window.handleMarkerSelected = function (cityName) {
        selectStation(cityName, true);
    };

    // -----------------------------------------------------------------------
    // 2. Fetch Environmental Telemetry (Live / Baseline)
    // -----------------------------------------------------------------------

    function loadStationTelemetry(cityName) {
        if (!cityName) return;

        if (btnFetchLive) {
            btnFetchLive.disabled = true;
            btnFetchLive.textContent = "⏳ Ingesting...";
        }

        fetch(`/api/weather/${encodeURIComponent(cityName)}`)
            .then(res => res.json())
            .then(payload => {
                if (payload.success && payload.data) {
                    const d = payload.data;

                    if (stationBadge) stationBadge.textContent = `${cityName} (${d.elevation_m}m MSL)`;
                    if (geoRiver) geoRiver.textContent = d.nearest_river;
                    if (geoCoords) geoCoords.textContent = `${d.latitude}°N, ${d.longitude}°E`;
                    if (geoDangerStage) geoDangerStage.textContent = `${d.danger_river_level_m} m`;
                    if (globalDataSource) globalDataSource.textContent = d.data_source;
                    if (inputs.dataSource) inputs.dataSource.value = d.data_source;
                    if (weatherCondition) weatherCondition.textContent = d.weather_condition || "Clear";

                    if (inputs.elevation) inputs.elevation.value = d.elevation_m;
                    if (inputs.distance) inputs.distance.value = d.distance_to_river_km;

                    // Update parameters
                    updateInput("rainfall", d.rainfall_mm, "mm");
                    updateInput("riverLevel", d.river_water_level_m, "m");
                    updateInput("soilMoisture", d.soil_moisture_pct, "%");
                    updateInput("drainage", d.drainage_capacity_pct || 65.0, "%");
                    updateInput("prevRain", d.prev_rainfall_7d_mm, "mm");
                    updateInput("temp", d.temp_c, "°C");
                    updateInput("humidity", d.humidity_pct, "%");

                    // Update live weather forecast cards and 24h hourly chart
                    if (forecastLiveIndicator) {
                        forecastLiveIndicator.textContent = d.is_live ? "🟢 Live Open-Meteo Telemetry" : "🟡 Regional Baseline (Offline Mode)";
                    }
                    if (d.daily_forecast) {
                        renderForecastCards(d.daily_forecast);
                    }
                    if (d.hourly_time_labels && d.hourly_rainfall_24h) {
                        updateHourlyChart(d.hourly_time_labels, d.hourly_rainfall_24h, cityName);
                    }

                    executePrediction(false);
                }
            })
            .catch(err => {
                console.error("[Telemetry Error] Failed to fetch environmental telemetry:", err);
            })
            .finally(() => {
                if (btnFetchLive) {
                    btnFetchLive.disabled = false;
                    btnFetchLive.textContent = "🔄 Refresh Live Weather";
                }
            });
    }

    if (btnFetchLive) {
        btnFetchLive.addEventListener("click", function () {
            const currentCity = locationSelect ? locationSelect.value : "Jalandhar";
            loadStationTelemetry(currentCity);
        });
    }

    // -----------------------------------------------------------------------
    // 3. Slider Binding & Value Display Updates
    // -----------------------------------------------------------------------

    function updateInput(key, val, unit) {
        if (inputs[key]) inputs[key].value = val;
        if (badges[key]) badges[key].textContent = `${val} ${unit}`;
    }

    function bindSlider(inputElem, badgeElem, unit) {
        if (!inputElem || !badgeElem) return;
        inputElem.addEventListener("input", function () {
            badgeElem.textContent = `${this.value} ${unit}`;
            if (inputs.dataSource) {
                inputs.dataSource.value = "Manual Parameter Simulation";
                if (globalDataSource) globalDataSource.textContent = "Manual Parameter Simulation";
            }
        });
    }

    bindSlider(inputs.rainfall, badges.rainfall, "mm");
    bindSlider(inputs.riverLevel, badges.riverLevel, "m");
    bindSlider(inputs.soilMoisture, badges.soilMoisture, "%");
    bindSlider(inputs.drainage, badges.drainage, "%");
    bindSlider(inputs.prevRain, badges.prevRain, "mm");
    bindSlider(inputs.temp, badges.temp, "°C");
    bindSlider(inputs.humidity, badges.humidity, "%");

    // -----------------------------------------------------------------------
    // 4. Simulation Mode & Advanced Scenario Presets
    // -----------------------------------------------------------------------

    if (toggleSimBtn) {
        toggleSimBtn.addEventListener("click", function () {
            isSimulationMode = !isSimulationMode;

            Object.values(inputs).forEach(inp => {
                if (inp && inp.type === "range") {
                    inp.disabled = !isSimulationMode;
                }
            });

            if (isSimulationMode) {
                this.classList.add("active");
                this.textContent = "🔒 Lock Parameters (Live Mode)";
                if (simPresetsPanel) simPresetsPanel.style.display = "block";
            } else {
                this.classList.remove("active");
                this.textContent = "✏️ Tweak Parameters (Simulation Mode)";
                if (simPresetsPanel) simPresetsPanel.style.display = "none";
            }
        });
    }

    document.querySelectorAll(".btn-preset").forEach(btn => {
        btn.addEventListener("click", function () {
            const scenario = this.getAttribute("data-scenario");
            applyScenarioPreset(scenario);
        });
    });

    function applyScenarioPreset(scenario) {
        if (inputs.dataSource) {
            inputs.dataSource.value = `Simulation: ${scenario.toUpperCase()}`;
            if (globalDataSource) globalDataSource.textContent = `Simulation (${scenario})`;
        }

        switch (scenario) {
            case "dry":
                updateInput("rainfall", 2.0, "mm");
                updateInput("riverLevel", 1.8, "m");
                updateInput("soilMoisture", 25.0, "%");
                updateInput("drainage", 85.0, "%");
                updateInput("prevRain", 4.0, "mm");
                updateInput("temp", 33.0, "°C");
                updateInput("humidity", 40.0, "%");
                break;
            case "monsoon":
                updateInput("rainfall", 115.0, "mm");
                updateInput("riverLevel", 2.9, "m");
                updateInput("soilMoisture", 84.0, "%");
                updateInput("drainage", 65.0, "%");
                updateInput("prevRain", 80.0, "mm");
                updateInput("temp", 28.0, "°C");
                updateInput("humidity", 85.0, "%");
                break;
            case "drainage_choke":
                updateInput("rainfall", 55.0, "mm");
                updateInput("riverLevel", 2.4, "m");
                updateInput("soilMoisture", 65.0, "%");
                updateInput("drainage", 22.0, "%"); // Heavily choked
                updateInput("prevRain", 35.0, "mm");
                updateInput("temp", 29.0, "°C");
                updateInput("humidity", 75.0, "%");
                break;
            case "river_surge":
                updateInput("rainfall", 20.0, "mm");
                updateInput("riverLevel", 5.2, "m"); // Surcharged river
                updateInput("soilMoisture", 60.0, "%");
                updateInput("drainage", 60.0, "%");
                updateInput("prevRain", 25.0, "mm");
                updateInput("temp", 26.5, "°C");
                updateInput("humidity", 70.0, "%");
                break;
            case "historic":
                updateInput("rainfall", 185.0, "mm");
                updateInput("riverLevel", 5.9, "m");
                updateInput("soilMoisture", 98.0, "%");
                updateInput("drainage", 18.0, "%");
                updateInput("prevRain", 260.0, "mm");
                updateInput("temp", 24.0, "°C");
                updateInput("humidity", 96.0, "%");
                break;
        }

        executePrediction(true);
    }

    // -----------------------------------------------------------------------
    // 5. Dual ML Inference Execution
    // -----------------------------------------------------------------------

    function executePrediction(scrollToResult = false) {
        const cityName = locationSelect ? locationSelect.value : "Jalandhar";

        const payload = {
            location_name: cityName,
            rainfall_mm: parseFloat(inputs.rainfall.value),
            river_water_level_m: parseFloat(inputs.riverLevel.value),
            soil_moisture_pct: parseFloat(inputs.soilMoisture.value),
            drainage_capacity_pct: parseFloat(inputs.drainage.value),
            prev_rainfall_7d_mm: parseFloat(inputs.prevRain.value),
            temp_c: parseFloat(inputs.temp.value),
            humidity_pct: parseFloat(inputs.humidity.value),
            elevation_m: parseFloat(inputs.elevation.value),
            distance_to_river_km: parseFloat(inputs.distance.value),
            data_source: inputs.dataSource.value || "Manual Input"
        };

        if (btnPredict) {
            btnPredict.disabled = true;
            btnPredict.textContent = "⚡ Running Dual Random Forest Inference...";
        }

        fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.result) {
                    renderPredictionResult(data.result);

                    if (typeof updateMarkerRisk === "function") {
                        updateMarkerRisk(
                            cityName,
                            data.result.prediction.risk_level,
                            data.result.prediction.risk_label,
                            data.result.prediction.confidence_pct,
                            data.result.inputs,
                            data.result.probable_cause.title
                        );
                    }

                    if (scrollToResult && resultBox) {
                        resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
                    }
                } else {
                    alert("Prediction error: " + (data.error || "Unknown server error"));
                }
            })
            .catch(err => {
                console.error("[Prediction Error] Inference failed:", err);
            })
            .finally(() => {
                if (btnPredict) {
                    btnPredict.disabled = false;
                    btnPredict.textContent = "Run Dual-Engine Machine Learning Assessment";
                }
            });
    }

    function renderPredictionResult(res) {
        const p = res.prediction;
        const cause = res.probable_cause;
        const xai = res.explainability;
        const hist = res.historical_comparison;

        // Update Risk Container Box
        if (resultBox) {
            resultBox.className = `result-box ${p.badge_class}`;
        }

        if (resultRiskLabel) resultRiskLabel.textContent = `${p.risk_label} Risk`;
        if (resultConfidenceBadge) resultConfidenceBadge.textContent = `${p.confidence_pct}% Confidence`;

        // Update Continuous Composite Risk Index (FEATURE 1)
        if (compositeScoreVal && p.composite_risk_score !== undefined) {
            compositeScoreVal.textContent = `${p.composite_risk_score} / 100`;
        }
        if (compositeScoreFill && p.composite_risk_score !== undefined) {
            compositeScoreFill.style.width = `${p.composite_risk_score}%`;
            compositeScoreFill.className = `composite-meter-fill ${p.badge_class}`;
        }

        // Update Cause-Aware Flood Classification Banner (FEATURE 2)
        if (causeBanner) {
            causeBanner.className = `cause-banner ${cause.badge_class}`;
        }
        if (causeTitle) causeTitle.textContent = cause.title;
        if (causeConfBadge) causeConfBadge.textContent = `${cause.confidence_pct}% Probable`;
        if (causeExplanation) causeExplanation.textContent = cause.explanation;

        // Render Corroborating Telemetry Evidence Checklist (FEATURE 2)
        if (causeEvidenceList && cause.supporting_factors) {
            causeEvidenceList.innerHTML = "";
            cause.supporting_factors.forEach(factorText => {
                const li = document.createElement("li");
                li.className = "cause-evidence-item";
                li.innerHTML = `<span class="cause-evidence-bullet">▸</span> ${factorText}`;
                causeEvidenceList.appendChild(li);
            });
        }

        // Update Historical Anomaly Badge
        if (historicalAnomalyBadge && hist) {
            historicalAnomalyBadge.className = `anomaly-pill ${hist.badge_class}`;
            historicalAnomalyBadge.textContent = `${hist.deviation_pct > 0 ? '+' : ''}${hist.deviation_pct}% vs Normal`;
        }

        // Update Probability Bars
        if (p.probabilities) {
            for (const [tier, pct] of Object.entries(p.probabilities)) {
                if (probBars[tier]) probBars[tier].style.width = `${pct}%`;
                if (probTexts[tier]) probTexts[tier].textContent = `${pct}%`;
            }
        }

        // Update Explainable AI (XAI) factors (FEATURE 6)
        if (xaiElevatingList && xai && xai.elevating_factors) {
            xaiElevatingList.innerHTML = "";
            xai.elevating_factors.forEach(f => {
                const div = document.createElement("div");
                div.className = "xai-factor-item elevating";
                div.innerHTML = `<span class="xai-icon">⚠️</span><span class="xai-text">${f}</span>`;
                xaiElevatingList.appendChild(div);
            });
        }

        // Update Advisories
        if (resultSummary) {
            resultSummary.innerHTML = `<strong>Assessment:</strong> ${p.summary}`;
        }
        if (resultAdvisory) resultAdvisory.textContent = p.advisory;
        if (resultAction) resultAction.textContent = p.action;

        if (resultTimestamp) {
            const now = new Date();
            resultTimestamp.textContent = `Inferred at ${now.toLocaleTimeString()} (DB Record #${res.db_id || "OK"})`;
        }
    }

    // -----------------------------------------------------------------------
    // 6. 3-Day Forecast Cards & 24h Hourly Rainfall Chart (FEATURE 4)
    // -----------------------------------------------------------------------

    function renderForecastCards(dailyForecast) {
        if (!forecastCardsContainer || !dailyForecast) return;
        forecastCardsContainer.innerHTML = "";
        dailyForecast.forEach(fc => {
            const card = document.createElement("div");
            card.className = "forecast-card";
            card.innerHTML = `
                <span class="forecast-day">${fc.day}</span>
                <span class="forecast-condition">${fc.condition}</span>
                <div class="forecast-metrics">
                    <span>🌡️ ${fc.temp_min}°C – ${fc.temp_max}°C</span>
                    <span class="forecast-rain">🌧️ ${fc.expected_rain_mm} mm</span>
                </div>
            `;
            forecastCardsContainer.appendChild(card);
        });
    }

    function initHourlyChart() {
        const canvas = document.getElementById("hourlyRainChart");
        if (!canvas) return;

        // Default initial 24h placeholder
        const labels = Array.from({ length: 24 }, (_, i) => `${String(i).padStart(2, '0')}:00`);
        const initialData = Array(24).fill(0.2);

        hourlyRainChart = new Chart(canvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Precipitation (mm/hr)",
                    data: initialData,
                    backgroundColor: "#00b4d8",
                    hoverBackgroundColor: "#48cae4",
                    borderRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `Rain: ${ctx.raw} mm`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#829ab1", font: { size: 9 }, maxTicksLimit: 12 },
                        grid: { display: false }
                    },
                    y: {
                        min: 0,
                        ticks: { color: "#829ab1", font: { size: 9 } },
                        grid: { color: "#1e2f5c" }
                    }
                }
            }
        });
    }

    function updateHourlyChart(labels, series, cityName) {
        if (hourlyStationName) hourlyStationName.textContent = cityName;
        if (!hourlyRainChart) {
            initHourlyChart();
        }
        if (hourlyRainChart) {
            hourlyRainChart.data.labels = labels || hourlyRainChart.data.labels;
            hourlyRainChart.data.datasets[0].data = series;
            hourlyRainChart.update();
        }
    }

    // -----------------------------------------------------------------------
    // 7. Interactive Sensitivity / What-If Analysis (FEATURE 6)
    // -----------------------------------------------------------------------

    function initWhatIfWidget() {
        document.querySelectorAll(".btn-whatif").forEach(btn => {
            btn.addEventListener("click", function () {
                const whatifType = this.getAttribute("data-whatif");
                runSensitivityScenario(whatifType);
            });
        });
    }

    function runSensitivityScenario(scenarioKey) {
        const cityName = locationSelect ? locationSelect.value : "Jalandhar";

        const baseFeatures = {
            rainfall_mm: parseFloat(inputs.rainfall.value),
            river_water_level_m: parseFloat(inputs.riverLevel.value),
            soil_moisture_pct: parseFloat(inputs.soilMoisture.value),
            drainage_capacity_pct: parseFloat(inputs.drainage.value),
            prev_rainfall_7d_mm: parseFloat(inputs.prevRain.value),
            temp_c: parseFloat(inputs.temp.value),
            humidity_pct: parseFloat(inputs.humidity.value),
            elevation_m: parseFloat(inputs.elevation.value),
            distance_to_river_km: parseFloat(inputs.distance.value)
        };

        let adjustment = {};
        switch (scenarioKey) {
            case "rain_25":
                adjustment = { rainfall_delta: 25.0 };
                break;
            case "rain_50":
                adjustment = { rainfall_delta: 50.0 };
                break;
            case "drainage_choke":
                adjustment = { drainage_delta: -30.0 };
                break;
            case "drainage_clear":
                adjustment = { drainage_delta: 30.0 };
                break;
            case "river_rise":
                adjustment = { river_delta: 1.0 };
                break;
            case "reset":
                if (whatifOutcomeCard) whatifOutcomeCard.style.display = "none";
                return;
        }

        if (whatifOutcomeCard) {
            whatifOutcomeCard.style.display = "block";
            whatifOutcomeCard.innerHTML = "<em>Calculating multivariate sensitivity response...</em>";
        }

        fetch("/api/sensitivity-analysis", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                location_name: cityName,
                base_features: baseFeatures,
                adjustment: adjustment
            })
        })
            .then(res => res.json())
            .then(d => {
                if (d.success && whatifOutcomeCard) {
                    const arrow = d.delta.score_change >= 0 ? "▲" : "▼";
                    const color = d.delta.score_change >= 0 ? "#ef4444" : "#10b981";
                    whatifOutcomeCard.innerHTML = `
                        <strong>Simulation Outcome:</strong> ${d.summary}
                        <div style="margin-top: 4px; font-size: 10px; color: ${color}; font-weight: 700;">
                            ${arrow} Risk Index Shift: ${d.delta.score_change > 0 ? '+' : ''}${d.delta.score_change} pts
                        </div>
                    `;
                }
            })
            .catch(err => {
                console.error("[What-If Error] Sensitivity calculation failed:", err);
            });
    }

    // -----------------------------------------------------------------------
    // 8. Multi-Station Comparison Modal & Chart (FEATURE 3)
    // -----------------------------------------------------------------------

    function initComparisonModal() {
        if (btnCompareStations && comparisonModal) {
            btnCompareStations.addEventListener("click", () => {
                comparisonModal.style.display = "flex";
                loadMultiStationComparison();
            });
        }

        if (btnCloseModal && comparisonModal) {
            btnCloseModal.addEventListener("click", () => {
                comparisonModal.style.display = "none";
            });
        }

        // Close on background backdrop click
        if (comparisonModal) {
            comparisonModal.addEventListener("click", (e) => {
                if (e.target === comparisonModal) {
                    comparisonModal.style.display = "none";
                }
            });
        }
    }

    function loadMultiStationComparison() {
        fetch("/api/compare-locations")
            .then(res => res.json())
            .then(data => {
                if (data.success && data.comparison) {
                    renderComparisonTable(data.comparison);
                    renderComparisonChart(data.comparison);
                }
            })
            .catch(err => console.error("[Comparison Error]", err));
    }

    function renderComparisonTable(comparisonList) {
        if (!comparisonTableBody) return;
        comparisonTableBody.innerHTML = "";

        comparisonList.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${item.name}</strong></td>
                <td>${item.district}</td>
                <td><span class="badge" style="background-color: ${item.color}22; color: ${item.color}; border: 1px solid ${item.color};">${item.risk_label}</span></td>
                <td class="font-mono font-bold" style="color: ${item.color};">${item.risk_score}%</td>
                <td class="font-mono">${item.rainfall_mm} mm</td>
                <td class="font-mono">${item.river_water_level_m}m / ${item.danger_river_level_m}m</td>
                <td class="font-mono">${item.drainage_capacity_pct}%</td>
                <td><span class="cause-tag-table">${item.probable_cause}</span></td>
                <td>
                    <button class="btn btn-outline btn-sm" onclick="selectStationAndClose('${item.name}')">Select</button>
                </td>
            `;
            comparisonTableBody.appendChild(tr);
        });
    }

    window.selectStationAndClose = function (cityName) {
        selectStation(cityName, true);
        if (comparisonModal) comparisonModal.style.display = "none";
    };

    function renderComparisonChart(comparisonList) {
        const canvas = document.getElementById("comparisonChart");
        if (!canvas) return;

        const labels = comparisonList.map(c => c.name);
        const scores = comparisonList.map(c => c.risk_score);
        const colors = comparisonList.map(c => c.color);

        if (comparisonChartInstance) {
            comparisonChartInstance.destroy();
        }

        comparisonChartInstance = new Chart(canvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Composite Risk Score (0–100%)",
                    data: scores,
                    backgroundColor: colors,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => `Risk Score: ${ctx.raw}%`
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#cbd5e1", font: { size: 10 } },
                        grid: { display: false }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { color: "#829ab1", font: { size: 10 } },
                        grid: { color: "#1e2f5c" }
                    }
                }
            }
        });
    }

    // -----------------------------------------------------------------------
    // 9. Emergency Alert Banner Verification (FEATURE 7)
    // -----------------------------------------------------------------------

    function initAlertBanner() {
        fetch("/api/alerts")
            .then(r => r.json())
            .then(d => {
                if (d.success && d.alerts) {
                    const unack = d.alerts.filter(a => !a.is_acknowledged && (a.alert_level === "High" || a.alert_level === "Severe"));
                    if (unack.length > 0 && emergencyAlertBanner && emergencyBannerText) {
                        const topAlert = unack[0];
                        emergencyBannerText.textContent = `${unack.length} Active High/Severe Alerts Detected! Latest: ${topAlert.title} (${topAlert.probable_cause})`;
                        emergencyAlertBanner.style.display = "flex";
                    }
                }
            })
            .catch(e => console.log("Alert banner query error:", e));

        if (btnDismissAlertBanner && emergencyAlertBanner) {
            btnDismissAlertBanner.addEventListener("click", () => {
                emergencyAlertBanner.style.display = "none";
            });
        }
    }

    // -----------------------------------------------------------------------
    // Initial Platform Bootstrap
    // -----------------------------------------------------------------------

    initHourlyChart();
    initWhatIfWidget();
    initComparisonModal();
    initAlertBanner();

    if (predictionForm) {
        predictionForm.addEventListener("submit", function (e) {
            e.preventDefault();
            executePrediction(true);
        });
    }
});
