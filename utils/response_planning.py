"""
=============================================================================
FLOOD DETECTION SYSTEM - CAUSE-AWARE RESPONSE PLANNING ENGINE
Generates transparent, rule-based emergency response priorities, evacuation
recommendations, resource allocations, and operational checklists tailored to
flood severity and the specific identified probable cause.
=============================================================================
"""


def generate_response_plan(risk_level, probable_cause_code, inputs, location_name, loc_meta):
    """
    Generate actionable disaster management plan based on severity and cause.
    
    :param risk_level: integer 0 (Low), 1 (Mod), 2 (High), 3 (Severe)
    :param probable_cause_code: integer 0 to 4
    :param inputs: dict of environmental features
    :param location_name: target Punjab city
    :param loc_meta: location metadata dictionary
    :return: dict with response planning directives
    """
    river_name = loc_meta.get("nearest_river", "local river")
    danger_lvl = loc_meta.get("danger_river_level_m", 4.5)
    current_river = inputs.get("river_water_level_m", 2.0)
    rainfall = inputs.get("rainfall_mm", 0.0)

    # 1. Emergency Response Priority
    if risk_level == 3:
        priority_label = "Priority 1 - Critical Emergency Response"
        priority_badge = "priority-critical"
        overall_stance = "RED ALERT: Immediate multi-agency mobilization required under District Disaster Management Authority (DDMA)."
    elif risk_level == 2:
        priority_label = "Priority 2 - High Alert & Embankment Reinforcement"
        priority_badge = "priority-high"
        overall_stance = "ORANGE ALERT: Pre-position rescue assets, issue riverside warnings, and maintain round-the-clock watch."
    elif risk_level == 1:
        priority_label = "Priority 3 - Active Monitoring & Drainage Patrol"
        priority_badge = "priority-medium"
        overall_stance = "YELLOW ALERT: Municipal teams inspect storm drains and vulnerable urban underpasses."
    else:
        priority_label = "Priority 4 - Routine Baseline Surveillance"
        priority_badge = "priority-low"
        overall_stance = "GREEN: Standard hydrologic monitoring within seasonal norms. No emergency deployment needed."

    # 2. Evacuation Priority & Zone Directives
    if risk_level == 3:
        evacuation_priority = "Immediate Evacuation of Floodplain & Riverbank Sectors"
        evacuation_zones = [
            f"Unprotected riverbeds and agricultural dhussi bunds along {river_name}.",
            f"Low-lying residential colonies within 2 km of {location_name} drainage outfalls.",
            "Basement facilities, ground-floor commercial zones, and informal settlements."
        ]
        evacuation_status = "Mandatory Evacuation Orders Activated"
    elif risk_level == 2:
        evacuation_priority = "Precautionary Standby Evacuation Advisory"
        evacuation_zones = [
            f"Riverside villages and settlements adjacent to {river_name}.",
            "Low-lying farmland susceptible to sheet wash and water pooling."
        ]
        evacuation_status = "Standby Notice Issued (Pack essentials, identify high ground)"
    elif risk_level == 1:
        evacuation_priority = "Advisory for Chronic Waterlogging Pockets"
        evacuation_zones = [
            "Low-elevation road underpasses and chronic street drainage choke points."
        ]
        evacuation_status = "No General Evacuation Required"
    else:
        evacuation_priority = "No Evacuation Required"
        evacuation_zones = ["All zones within standard safety parameters."]
        evacuation_status = "Normal Operations"

    # 3. Drainage Inspection & Hydraulic Operations
    if probable_cause_code in [2, 4]:  # Drainage-driven or Combined
        drainage_priority = "Critical Priority - Immediate Mechanical De-watering & Desilting"
        drainage_actions = [
            f"Deploy high-capacity diesel suction pumps to primary bottlenecks (e.g., Buddha Nullah outfalls if in Ludhiana).",
            "Clear debris and plastic blockages at all municipal culvert grates and sluice gates.",
            "Divert incoming storm runoff into retention basins and secondary agricultural drains.",
            "Verify backup diesel power for all municipal stormwater pumping stations."
        ]
    elif probable_cause_code == 3:  # River overflow
        drainage_priority = "River Sluice Gate Control & Backflow Prevention"
        drainage_actions = [
            "Shut non-return flap valves on municipal drains connecting to the river to prevent reverse backflow into city streets.",
            f"Monitor water gauge pressure on {river_name} embankments every 30 minutes.",
            "Patrol dykes (dhussi bunds) for seepage, piping holes, or sand boils."
        ]
    else:
        drainage_priority = "Routine Maintenance & Inspection"
        drainage_actions = [
            "Standard culvert sweep and trash rack inspection.",
            "Log water depth telemetry at key monitoring culverts."
        ]

    # 4. Emergency Resource Allocation
    if risk_level == 3:
        resources = {
            "ndrf_sdrf_teams": "3 Battalions (NDRF / SDRF) with motorized inflatable rescue boats",
            "dewatering_pumps": "18 High-capacity (100+ HP) mobile diesel de-watering pumps",
            "sandbag_reserve": "45,000 Heavy geotextile sandbags for breach plug operations",
            "relief_shelters": "8 Designated cyclone/flood relief centers & community schools activated",
            "medical_units": "4 Mobile public health emergency teams equipped with water purification tablets"
        }
    elif risk_level == 2:
        resources = {
            "ndrf_sdrf_teams": "1 Battalion on standby at district police headquarters",
            "dewatering_pumps": "8 Mobile trailer-mounted de-watering pump sets",
            "sandbag_reserve": "15,000 Sandbags pre-staged at vulnerable bund locations",
            "relief_shelters": "3 Community centers identified and kept on 2-hour standby",
            "medical_units": "2 Paramedic rapid response squads on standby"
        }
    elif risk_level == 1:
        resources = {
            "ndrf_sdrf_teams": "State disaster teams notified on standard operational standby",
            "dewatering_pumps": "4 Municipal road-clearing pump vehicles deployed",
            "sandbag_reserve": "3,000 Sandbags in municipal inventory",
            "relief_shelters": "Standard facilities cataloged",
            "medical_units": "Routine clinic advisory active"
        }
    else:
        resources = {
            "ndrf_sdrf_teams": "Standard barracks availability",
            "dewatering_pumps": "2 Maintenance pump sets on routine standby",
            "sandbag_reserve": "Standard municipal stockpile",
            "relief_shelters": "Standard municipal shelters inactive",
            "medical_units": "Normal district healthcare capacity"
        }

    # 5. Operational Action Checklist for Authorities
    checklist = []
    if risk_level >= 2:
        checklist.append(f"Establish Emergency Operations Center (EOC) in {location_name} with 24/7 communications.")
        checklist.append(f"Coordinate with Central Water Commission (CWC) and Bhakra Beas Management Board (BBMB) for dam discharge updates.")
        checklist.append("Issue emergency broadcast via local FM radio, community loudspeakers, and SMS alert channels.")
        checklist.append(f"Restrict heavy vehicular traffic near {river_name} bridge crossings and flooded causeways.")
        checklist.append("Pre-position food packets, clean drinking water tankers, and portable generators at relief centers.")
    elif risk_level == 1:
        checklist.append(f"Issue traffic diversion advisories for waterlogged road stretches in {location_name}.")
        checklist.append("Dispatch municipal jetting and suction machines to unclog flooded intersections.")
        checklist.append("Notify agricultural extension officers to assess standing crop pooling.")
    else:
        checklist.append("Maintain routine hourly telemetry collection.")
        checklist.append("Verify sensor battery levels and communication links.")

    return {
        "emergency_priority": priority_label,
        "priority_badge": priority_badge,
        "overall_stance": overall_stance,
        "evacuation_priority": evacuation_priority,
        "evacuation_status": evacuation_status,
        "evacuation_zones": evacuation_zones,
        "drainage_priority": drainage_priority,
        "drainage_actions": drainage_actions,
        "resources": resources,
        "action_checklist": checklist
    }
