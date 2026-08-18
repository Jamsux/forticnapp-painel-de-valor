"""Coleta de vulnerabilidades ativas em hosts (Vulnerabilities/Hosts)."""
import datetime as dt
import pandas as pd

SEVERITIES = ["Critical", "High", "Medium", "Low", "Info"]


def _window(now, lookback_days=1):
    now = now or dt.datetime.now(dt.timezone.utc)
    start = now - dt.timedelta(days=lookback_days)
    return {
        "startTime": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def fetch_severity_counts(client, now=None, lookback_days=1):
    """Conta total de avaliações ativas por severidade sem baixar todas as linhas."""
    counts = {}
    time_filter = _window(now, lookback_days)
    for sev in SEVERITIES:
        body = {
            "timeFilter": time_filter,
            "filters": [
                {"field": "status", "expression": "eq", "value": "Active"},
                {"field": "severity", "expression": "eq", "value": sev},
            ],
            "returns": ["vulnId"],
        }
        resp = client.post("/api/v2/Vulnerabilities/Hosts/search", body)
        counts[sev] = resp.get("paging", {}).get("totalRows", len(resp.get("data", [])))
    return counts


def _flatten(row):
    props = row.get("props", {}) or {}
    fix = row.get("fixInfo", {}) or {}
    eval_ctx = row.get("evalCtx", {}) or {}
    risk_breakdown = (row.get("hostRiskInfo", {}) or {}).get("host_risk_factors_breakdown", {}) or {}
    exploit = risk_breakdown.get("exploit_summary", {}) or {}
    return {
        "mid": row.get("mid"),
        "hostname": eval_ctx.get("hostname"),
        "vulnId": row.get("vulnId"),
        "severity": row.get("severity"),
        "status": row.get("status"),
        "cveRiskScore": row.get("cveRiskScore"),
        "hostRiskScore": row.get("hostRiskScore"),
        "fixAvailable": fix.get("fix_available") == "1",
        "fixedVersion": fix.get("fixed_version"),
        "firstTimeSeen": props.get("first_time_seen"),
        "exploitPublic": exploit.get("exploit_public"),
        "disclosureInWild": exploit.get("disclosure_in_wild"),
        "exploitVirusMalware": exploit.get("exploit_virus_malware"),
        "exploitWormified": exploit.get("exploit_wormified"),
        "startTime": row.get("startTime"),
    }


def fetch_critical_high_detail(client, now=None, lookback_days=1, max_pages=25):
    """Baixa o detalhe das avaliações Critical/High ativas (deduplicado por host+CVE)."""
    body = {
        "timeFilter": _window(now, lookback_days),
        "filters": [
            {"field": "status", "expression": "eq", "value": "Active"},
            {"field": "severity", "expression": "in", "values": ["Critical", "High"]},
        ],
    }
    rows = client.search_all_pages("/api/v2/Vulnerabilities/Hosts/search", body, max_pages=max_pages)
    if not rows:
        return pd.DataFrame(columns=list(_flatten({}).keys()))
    df = pd.DataFrame([_flatten(r) for r in rows])
    df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce", utc=True)
    df["firstTimeSeen"] = pd.to_datetime(df["firstTimeSeen"], errors="coerce", utc=True)
    df = df.sort_values("startTime").drop_duplicates(subset=["mid", "vulnId"], keep="last")
    return df
