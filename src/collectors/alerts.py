"""Coleta de Alertas (unifica sinais de CSPM/Policy, comportamento/Anomaly e Composite/Threat Detection)."""
import datetime as dt
import pandas as pd


def _flatten(row):
    derived = row.get("derivedFields", {}) or {}
    info = row.get("alertInfo", {}) or {}
    return {
        "alertId": row.get("alertId"),
        "alertName": row.get("alertName"),
        "alertType": row.get("alertType"),
        "severity": row.get("severity"),
        "status": row.get("status"),
        "category": derived.get("category"),
        "subCategory": derived.get("sub_category"),
        "source": derived.get("source"),
        "startTime": row.get("startTime"),
        "endTime": row.get("endTime"),
        "lastUserUpdatedTime": row.get("lastUserUpdatedTime"),
        "policyId": row.get("policyId"),
        "description": info.get("subject") or info.get("description"),
        "internetExposure": row.get("internetExposure"),
        "reachability": row.get("reachability"),
    }


def fetch_alerts(client, days=90, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=days)
    rows = client.search_time_windows(
        "/api/v2/Alerts/search",
        base_body={},
        start=start,
        end=now,
        window_days=7,
    )
    if not rows:
        return pd.DataFrame(columns=list(_flatten({}).keys()))
    df = pd.DataFrame([_flatten(r) for r in rows]).drop_duplicates(subset=["alertId"])
    for col in ("startTime", "endTime", "lastUserUpdatedTime"):
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    return df
