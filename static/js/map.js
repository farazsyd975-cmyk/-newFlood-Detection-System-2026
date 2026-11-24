/**
 * ==============================================================================
 * FLOOD DETECTION SYSTEM - ADVANCED LEAFLET.JS MAP MODULE
 * Interactive Punjab OpenStreetMap with dynamic risk pins, buffer zones,
 * and critical flood hotspot overlays.
 * ==============================================================================
 */

const PUNJAB_CENTER = [31.2500, 75.5000];
const DEFAULT_ZOOM = 8;

let floodMap = null;
const stationMarkers = {};
const riskBufferCircles = {};
let hotspotLayerGroup = null;
let hotspotsVisible = false;

// Critical Punjab Flood Hotspots Catalog
const CRITICAL_HOTSPOTS = [
    {
        name: "Harike Pattan Wetland & Confluence",
        lat: 31.1550,
        lon: 74.9580,
        type: "Confluence Backwater",
        desc: "Sutlej-Beas confluence; severe backwater ponding affecting Kapurthala & Firozpur Mand areas."
    },
    {
        name: "Buddha Nullah Industrial Outfall",
        lat: 30.9320,
        lon: 75.8250,
        type: "Urban Drainage Choke",
        desc: "Ludhiana storm channel chronic choke; overflows into dense industrial and residential wards."
    },
    {
        name: "Shivalik Seasonal Torrents (Choes)",
        lat: 31.5450,
        lon: 75.9550,
        type: "Flash Torrent Basin",
        desc: "Steep sub-mountainous torrents in Hoshiarpur carrying heavy silt and flash runoff."
    },
    {
        name: "Sutlej Dhussi Bunds Corridor",
        lat: 31.0800,
        lon: 76.1500,
        type: "River Embankment Dykes",
        desc: "Vulnerable earthern dykes near Nawanshahr & Phillaur downstream of Ropar Barrage."
    }
];

/**
 * Initialize Leaflet OpenStreetMap
 */
function initFloodMap() {
    const mapElement = document.getElementById("punjab-map");
    if (!mapElement) return;

    floodMap = L.map("punjab-map", {
        center: PUNJAB_CENTER,
        zoom: DEFAULT_ZOOM,
        minZoom: 7,
        maxZoom: 14,
        scrollWheelZoom: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Punjab Flood Intelligence Platform',
        maxZoom: 18
    }).addTo(floodMap);

    hotspotLayerGroup = L.layerGroup().addTo(floodMap);

    loadMapMarkers();

    const resetBtn = document.getElementById("btn-reset-map");
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            floodMap.flyTo(PUNJAB_CENTER, DEFAULT_ZOOM, { duration: 1.0 });
        });
    }

    const hotspotBtn = document.getElementById("btn-toggle-hotspots");
    if (hotspotBtn) {
        hotspotBtn.addEventListener("click", toggleHotspots);
    }
}

/**
 * Fetch and place station markers from backend
 */
function loadMapMarkers() {
    fetch("/api/map-markers")
        .then(res => res.json())
        .then(data => {
            if (data.success && data.markers) {
                data.markers.forEach(station => {
                    createStationMarker(station);
                });
            }
        })
        .catch(err => {
            console.error("[Map Error] Could not load station markers:", err);
        });
}

/**
 * Create custom HTML pin marker and dynamic risk radius ring
 */
function createStationMarker(station) {
    const color = getRiskColor(station.risk_level);

    // Custom circle pulse icon
    const customIcon = L.divIcon({
        className: "custom-station-pin",
        html: `<div class="pin-pulse" id="pin-${slugify(station.name)}" style="background-color: ${color};"></div>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13],
        popupAnchor: [0, -14]
    });

    const marker = L.marker([station.latitude, station.longitude], { icon: customIcon }).addTo(floodMap);
    marker.bindPopup(generatePopupHtml(station));

    // Dynamic risk buffer circle overlay (spatial radius representing district alert buffer)
    const radiusMeters = getRiskRadiusMeters(station.risk_level);
    const bufferCircle = L.circle([station.latitude, station.longitude], {
        radius: radiusMeters,
        color: color,
        fillColor: color,
        fillOpacity: station.risk_level === 0 ? 0.08 : 0.22,
        weight: 1.5,
        dashArray: station.risk_level >= 2 ? "4, 6" : null
    }).addTo(floodMap);

    stationMarkers[station.name] = {
        markerInstance: marker,
        bufferCircle: bufferCircle,
        data: station
    };

    marker.on("click", () => {
        if (window.handleMarkerSelected) {
            window.handleMarkerSelected(station.name);
        }
    });
}

/**
 * Generate rich popup with Cause-Aware tag, rainfall, river level & drainage
 */
function generatePopupHtml(station) {
    const badgeClass = getRiskBadgeClass(station.risk_level);
    const causeTitle = station.probable_cause || "Normal Drainage";

    return `
        <div class="popup-card">
            <div class="popup-header">
                <div class="popup-city">${station.name} (${station.district})</div>
                <div class="popup-coords">${station.latitude}°N, ${station.longitude}°E • ${station.elevation_m}m MSL</div>
            </div>
            <div class="popup-cause-row">
                <span class="p-lbl">Probable Cause:</span>
                <span class="cause-tag-table">${causeTitle}</span>
            </div>
            <div class="popup-metrics">
                <div class="popup-metric">
                    <span class="p-lbl">24h Rain</span>
                    <span class="p-val font-mono">${station.rainfall_mm} mm</span>
                </div>
                <div class="popup-metric">
                    <span class="p-lbl">River Level</span>
                    <span class="p-val font-mono">${station.river_water_level_m} / ${station.danger_river_level_m}m</span>
                </div>
                <div class="popup-metric">
                    <span class="p-lbl">Drainage</span>
                    <span class="p-val font-mono">${station.drainage_capacity_pct || 65}%</span>
                </div>
                <div class="popup-metric">
                    <span class="p-lbl">Risk Tier</span>
                    <span class="badge ${badgeClass}">${station.risk_label}</span>
                </div>
            </div>
            <button class="popup-btn" onclick="selectStationFromPopup('${station.name}')">
                Analyze This Station ➔
            </button>
        </div>
    `;
}

/**
 * Toggle critical Punjab flood hotspot overlays
 */
function toggleHotspots() {
    hotspotsVisible = !hotspotsVisible;
    const btn = document.getElementById("btn-toggle-hotspots");

    if (hotspotsVisible) {
        if (btn) btn.classList.add("active");
        CRITICAL_HOTSPOTS.forEach(hs => {
            const hsIcon = L.divIcon({
                className: "custom-hotspot-pin",
                html: `<div class="hotspot-pulse">⚠️</div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
            const hsMarker = L.marker([hs.lat, hs.lon], { icon: hsIcon });
            hsMarker.bindPopup(`
                <div class="popup-card">
                    <div class="popup-header">
                        <div class="popup-city">⚠️ ${hs.name}</div>
                        <div class="popup-coords">Category: ${hs.type}</div>
                    </div>
                    <p class="text-sm text-secondary" style="margin: 6px 0;">${hs.desc}</p>
                </div>
            `);
            hotspotLayerGroup.addLayer(hsMarker);
        });
    } else {
        if (btn) btn.classList.remove("active");
        hotspotLayerGroup.clearLayers();
    }
}

/**
 * Update marker color, buffer ring, and popup content dynamically
 */
function updateMarkerRisk(stationName, riskLevel, riskLabel, confidencePct, inputs, causeTitle) {
    const item = stationMarkers[stationName];
    if (!item) return;

    const color = getRiskColor(riskLevel);
    const pinElem = document.getElementById(`pin-${slugify(stationName)}`);
    if (pinElem) {
        pinElem.style.backgroundColor = color;
    }

    // Update risk buffer circle
    if (item.bufferCircle) {
        const radiusMeters = getRiskRadiusMeters(riskLevel);
        item.bufferCircle.setRadius(radiusMeters);
        item.bufferCircle.setStyle({
            color: color,
            fillColor: color,
            fillOpacity: riskLevel === 0 ? 0.08 : 0.22,
            dashArray: riskLevel >= 2 ? "4, 6" : null
        });
    }

    // Update stored data
    item.data.risk_level = riskLevel;
    item.data.risk_label = riskLabel;
    item.data.confidence_pct = confidencePct;
    if (causeTitle) item.data.probable_cause = causeTitle;
    if (inputs) {
        item.data.rainfall_mm = inputs.rainfall_mm;
        item.data.river_water_level_m = inputs.river_water_level_m;
        item.data.drainage_capacity_pct = inputs.drainage_capacity_pct;
    }

    item.markerInstance.setPopupContent(generatePopupHtml(item.data));
}

function centerMapOnStation(stationName) {
    const item = stationMarkers[stationName];
    if (item && floodMap) {
        const coords = [item.data.latitude, item.data.longitude];
        floodMap.flyTo(coords, 10, { duration: 1.0 });
        item.markerInstance.openPopup();
    }
}

function selectStationFromPopup(stationName) {
    if (window.handleMarkerSelected) {
        window.handleMarkerSelected(stationName);
    }
}

function getRiskRadiusMeters(level) {
    switch (parseInt(level)) {
        case 0: return 5000;
        case 1: return 8500;
        case 2: return 14000;
        case 3: return 20000;
        default: return 5000;
    }
}

function getRiskColor(level) {
    switch (parseInt(level)) {
        case 0: return "#16a34a"; // Green
        case 1: return "#ca8a04"; // Amber Yellow
        case 2: return "#ea580c"; // Vivid Orange
        case 3: return "#dc2626"; // Emergency Red
        default: return "#16a34a";
    }
}

function getRiskBadgeClass(level) {
    switch (parseInt(level)) {
        case 0: return "badge-low";
        case 1: return "badge-mod";
        case 2: return "badge-high";
        case 3: return "badge-sev";
        default: return "badge-low";
    }
}

function slugify(text) {
    return text.toString().toLowerCase().replace(/\s+/g, "-").replace(/[^\w\-]+/g, "");
}

document.addEventListener("DOMContentLoaded", initFloodMap);
