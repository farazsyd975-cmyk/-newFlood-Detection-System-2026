"""
=============================================================================
FLOOD DETECTION SYSTEM - EARLY WARNING & ALERT SYSTEM
Generates and manages location-specific high and severe flood hazard alerts,
tracks escalation, and maintains an audit log in SQLite.
=============================================================================
"""

from datetime import datetime
from database.db import save_alert, get_alerts, acknowledge_alert, acknowledge_all_alerts, get_location_latest_predictions


def evaluate_and_record_alert(prediction_result):
    """
    Evaluate if prediction warrants an early warning alert, detect risk escalation,
    and persist to SQLite if High or Severe.
    """
    pred = prediction_result.get("prediction", {})
    risk_level = pred.get("risk_level", 0)
    risk_label = pred.get("risk_label", "Low")
    loc_name = prediction_result.get("location_name", "Unknown")
    cause_info = prediction_result.get("probable_cause", {})
    cause_title = cause_info.get("title", "Normal Drainage")

    # Only High (2) and Severe (3) trigger formal early warning alerts
    if risk_level >= 2:
        is_escalation = 0
        previous_risk_level = None

        try:
            latest_records = get_location_latest_predictions()
            if loc_name in latest_records:
                prev_record = latest_records[loc_name]
                prev_level = prev_record.get("risk_level", 0)
                previous_risk_level = prev_record.get("risk_label", "Low")
                if risk_level > prev_level:
                    is_escalation = 1
        except Exception:
            pass

        if is_escalation:
            title = f"🚨 [ESCALATION] {risk_label.upper()} FLOOD HAZARD: {loc_name}"
            prefix = f"RISK ESCALATION DETECTED: Condition upgraded from {previous_risk_level} to {risk_label}. "
        else:
            title = f"{risk_label.upper()} FLOOD RISK ALERT: {loc_name}"
            prefix = ""

        if risk_level == 3:
            msg = f"{prefix}CRITICAL EMERGENCY: Severe flood hazard identified for {loc_name}. Probable Cause: {cause_title}. Water levels or intense rainfall exceeding safety thresholds. Immediate disaster response deployment recommended."
        else:
            msg = f"{prefix}WARNING: High flood hazard identified for {loc_name}. Probable Cause: {cause_title}. River gauge approaching warning mark or heavy overland saturation. Precautionary monitoring and bund protection advised."

        try:
            alert_id = save_alert(
                location_name=loc_name,
                alert_level=risk_label,
                title=title,
                message=msg,
                probable_cause=cause_title,
                is_escalation=is_escalation,
                previous_risk_level=previous_risk_level
            )
            return {
                "alert_triggered": True,
                "alert_id": alert_id,
                "level": risk_label,
                "title": title,
                "message": msg,
                "is_escalation": bool(is_escalation),
                "previous_risk_level": previous_risk_level
            }
        except Exception as e:
            print(f"[Alert System Warning] Failed to log alert: {e}")

    return {"alert_triggered": False}
