"""Transforma os dados brutos cacheados em indicadores prontos para os dashboards."""
import datetime as dt
import pandas as pd


def _now():
    return dt.datetime.now(dt.timezone.utc)


# ------------------------------------------------------------- Período ----

# A API só devolve alertas dos últimos 90 dias ("startTime has to be within the
# past 90 Days"), então não existe recorte anterior a isso — nem via nova coleta.
RETENTION_DAYS = 90


def filter_by_period(alerts_df, start=None, end=None):
    """Recorta os alertas por data de criação. Os demais conjuntos (vulnerabilidades,
    inventário) são fotografia do momento da coleta e não têm recorte temporal."""
    if alerts_df is None or alerts_df.empty:
        return alerts_df
    df = alerts_df
    if start is not None:
        df = df[df["startTime"] >= pd.Timestamp(start)]
    if end is not None:
        df = df[df["startTime"] <= pd.Timestamp(end)]
    return df


def period_over_period(alerts_df, start, end):
    """Compara o período escolhido com o período imediatamente anterior de mesma
    duração. Devolve delta=None quando o período anterior cai fora do que foi
    coletado — melhor não mostrar variação do que mostrar uma queda falsa."""
    empty = {"current": 0, "previous": None, "delta": None, "delta_pct": None}
    if alerts_df is None or alerts_df.empty or start is None or end is None:
        return empty
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    duration = end - start
    prev_start, prev_end = start - duration, start
    current = len(filter_by_period(alerts_df, start, end))

    data_start = alerts_df["startTime"].min()
    if prev_start < data_start:
        return {"current": current, "previous": None, "delta": None, "delta_pct": None}

    previous = len(alerts_df[(alerts_df["startTime"] >= prev_start) & (alerts_df["startTime"] < prev_end)])
    delta = current - previous
    return {
        "current": current,
        "previous": previous,
        "delta": delta,
        "delta_pct": round(100 * delta / previous, 1) if previous else None,
    }


# ---------------------------------------------------------------- Alertas --

def alert_headline_kpis(alerts_df, now=None):
    """`now` é a referência para calcular há quanto tempo os alertas estão abertos.
    Mesmo olhando um período passado, o que interessa é há quanto tempo estão
    parados até hoje — por isso o padrão é o instante atual."""
    if alerts_df is None or alerts_df.empty:
        return {
            "total": 0, "open": 0, "open_pct": 0.0,
            "critical_high_open": 0, "avg_open_age_days": 0.0,
        }
    now = now or _now()
    open_df = alerts_df[alerts_df["status"] == "Open"]
    crit_high_open = open_df[open_df["severity"].isin(["Critical", "High"])]
    age_days = (now - open_df["startTime"]).dt.total_seconds() / 86400
    total = len(alerts_df)
    return {
        "total": total,
        "open": len(open_df),
        "open_pct": round(100 * len(open_df) / total, 1) if total else 0.0,
        "critical_high_open": len(crit_high_open),
        "avg_open_age_days": round(age_days.mean(), 1) if len(open_df) else 0.0,
    }


def resolution_time_kpis(alerts_df, touched_tolerance_minutes=5):
    """MTTR (mediana/p90) a partir de alertas Closed, usando
    (lastUserUpdatedTime - startTime) como proxy do tempo até o fechamento.

    MTTA/MTTD não são calculados aqui: a API não expõe um evento distinto de
    'reconhecimento' (apenas criação -> fechamento) nem o instante real em que
    o problema subjacente começou, então qualquer número seria inventado.
    Em vez disso, reportamos o quanto dos alertas abertos nunca tiveram
    qualquer atualização registrada desde a criação (gap de reconhecimento).
    """
    empty = {
        "sample_size": 0, "mttr_hours_median": 0.0, "mttr_days_median": 0.0,
        "mttr_hours_p90": 0.0, "mttr_days_p90": 0.0,
        "open_total": 0, "open_never_touched": 0, "open_never_touched_pct": 0.0,
    }
    if alerts_df is None or alerts_df.empty:
        return empty

    closed = alerts_df[alerts_df["status"] == "Closed"].copy()
    closed["ttr_hours"] = (closed["lastUserUpdatedTime"] - closed["startTime"]).dt.total_seconds() / 3600
    closed = closed[closed["ttr_hours"] >= 0]

    open_df = alerts_df[alerts_df["status"] == "Open"].copy()
    touched = (open_df["lastUserUpdatedTime"] - open_df["startTime"]) > pd.Timedelta(minutes=touched_tolerance_minutes)
    never_touched = int((~touched).sum())

    if closed.empty:
        result = dict(empty)
        result["open_total"] = len(open_df)
        result["open_never_touched"] = never_touched
        result["open_never_touched_pct"] = round(100 * never_touched / len(open_df), 1) if len(open_df) else 0.0
        return result

    median_h = closed["ttr_hours"].median()
    p90_h = closed["ttr_hours"].quantile(0.9)
    return {
        "sample_size": len(closed),
        "mttr_hours_median": round(median_h, 1),
        "mttr_days_median": round(median_h / 24, 1),
        "mttr_hours_p90": round(p90_h, 1),
        "mttr_days_p90": round(p90_h / 24, 1),
        "open_total": len(open_df),
        "open_never_touched": never_touched,
        "open_never_touched_pct": round(100 * never_touched / len(open_df), 1) if len(open_df) else 0.0,
    }


def response_bias_note(period_days, sample_size, retention=RETENTION_DAYS):
    """Aviso quando o período é curto demais para julgar a capacidade de resposta.

    O recorte é pela data de CRIAÇÃO do alerta. Numa janela curta, só entram como
    'fechados' os alertas que nasceram e foram encerrados dentro dela — os que
    demoram ficam de fora. Isso infla o '% em aberto' e derruba o tempo de
    resolução. Sem este aviso, um recorte de 7 dias exibiria 'MTTR de 0 dias' e
    '100% em aberto' como se fossem boas/más notícias reais.
    """
    from .i18n import t

    if sample_size == 0:
        return t("bias.no_sample")
    if period_days < retention / 2:
        return t("bias.short_period", days=retention)
    return None


def mttr_by_severity(alerts_df):
    if alerts_df is None or alerts_df.empty:
        return pd.DataFrame(columns=["severity", "mttr_days"])
    closed = alerts_df[alerts_df["status"] == "Closed"].copy()
    if closed.empty:
        return pd.DataFrame(columns=["severity", "mttr_days"])
    closed["ttr_hours"] = (closed["lastUserUpdatedTime"] - closed["startTime"]).dt.total_seconds() / 3600
    closed = closed[closed["ttr_hours"] >= 0]
    grouped = closed.groupby("severity")["ttr_hours"].median().reset_index()
    grouped["mttr_days"] = (grouped["ttr_hours"] / 24).round(1)
    order = {s: i for i, s in enumerate(SEVERITY_ORDER)}
    grouped["_order"] = grouped["severity"].map(order).fillna(99)
    return grouped.sort_values("_order")[["severity", "mttr_days"]].reset_index(drop=True)


def alerts_weekly_trend(alerts_df):
    if alerts_df is None or alerts_df.empty:
        return pd.DataFrame(columns=["week", "total", "critical_high"])
    df = alerts_df.copy()
    df["week"] = df["startTime"].dt.tz_convert(None).dt.to_period("W").dt.start_time
    weekly = df.groupby("week").agg(
        total=("alertId", "count"),
        critical_high=("severity", lambda s: s.isin(["Critical", "High"]).sum()),
    ).reset_index()
    return weekly.sort_values("week")


def alerts_by_category(alerts_df):
    if alerts_df is None or alerts_df.empty:
        return pd.DataFrame(columns=["category", "count"])
    return (
        alerts_df.groupby("category").size().reset_index(name="count").sort_values("count", ascending=False)
    )


def top_alert_types(alerts_df, n=10):
    if alerts_df is None or alerts_df.empty:
        return pd.DataFrame(columns=["alertType", "count"])
    return (
        alerts_df.groupby("alertType").size().reset_index(name="count")
        .sort_values("count", ascending=False).head(n)
    )


def open_alerts_table(alerts_df):
    if alerts_df is None or alerts_df.empty:
        return pd.DataFrame()
    now = _now()
    open_df = alerts_df[alerts_df["status"] == "Open"].copy()
    open_df["age_days"] = ((now - open_df["startTime"]).dt.total_seconds() / 86400).round(1)
    cols = ["alertId", "alertName", "severity", "category", "alertType", "age_days", "startTime", "description"]
    return open_df[cols].sort_values(["severity", "age_days"], ascending=[True, False])


# --------------------------------------------------------- Vulnerabilidades --

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Info"]


# disclosure_in_wild volta "Yes" em praticamente 100% das avaliações desta API
# (verificado empiricamente numa amostra de 5.000 linhas) — não discrimina nada e
# infla "exploit conhecido" para ~97% de tudo. Não é usado abaixo. exploit_public
# (existe PoC público) e exploit_virus_malware (uso confirmado por malware/
# ransomware) são os sinais que de fato diferenciam prioridade.
def _known_exploited_mask(df):
    return (df["exploitPublic"] == "Yes") | (df["exploitVirusMalware"] == "Yes")


def vuln_kpis(vuln_severity_counts, vuln_detail_df):
    counts = vuln_severity_counts or {}
    total_active = sum(counts.values())
    critical_high_active = counts.get("Critical", 0) + counts.get("High", 0)
    if vuln_detail_df is None or vuln_detail_df.empty:
        return {
            "counts": counts, "total_active": total_active,
            "critical_high_active": critical_high_active,
            "known_exploited": 0, "malware_associated": 0, "wormable": 0,
            "fixable_now": 0, "hosts_affected": 0,
        }
    known_exploited = vuln_detail_df[_known_exploited_mask(vuln_detail_df)]
    malware_associated = vuln_detail_df[vuln_detail_df["exploitVirusMalware"] == "Yes"]
    wormable = vuln_detail_df[vuln_detail_df["exploitWormified"] == "Yes"]
    fixable = vuln_detail_df[vuln_detail_df["fixAvailable"]]
    return {
        "counts": counts,
        "total_active": total_active,
        "critical_high_active": critical_high_active,
        "known_exploited": len(known_exploited),
        "malware_associated": len(malware_associated),
        "wormable": len(wormable),
        "fixable_now": len(fixable),
        "hosts_affected": vuln_detail_df["mid"].nunique(),
    }


def top_vulnerable_hosts(vuln_detail_df, n=10):
    if vuln_detail_df is None or vuln_detail_df.empty:
        return pd.DataFrame(columns=["hostname", "critical", "high", "total"])
    df = vuln_detail_df.copy()
    grouped = df.groupby("hostname")["severity"].value_counts().unstack(fill_value=0)
    for sev in ("Critical", "High"):
        if sev not in grouped.columns:
            grouped[sev] = 0
    grouped["total"] = grouped.sum(axis=1)
    grouped = grouped.rename(columns={"Critical": "critical", "High": "high"})
    return grouped[["critical", "high", "total"]].sort_values(
        ["critical", "high"], ascending=False
    ).reset_index().head(n)


def known_exploited_table(vuln_detail_df, n=25):
    if vuln_detail_df is None or vuln_detail_df.empty:
        return pd.DataFrame()
    df = vuln_detail_df[_known_exploited_mask(vuln_detail_df)].copy()
    cols = ["hostname", "vulnId", "severity", "cveRiskScore", "fixAvailable", "fixedVersion", "startTime"]
    return df[cols].sort_values("cveRiskScore", ascending=False).head(n)


# -------------------------------------------------------------- Cobertura --

def _cloud_account_key(account):
    """A API 'CloudAccounts' lista uma linha por INTEGRAÇÃO (ex: logs de atividade
    + avaliação de configuração), não uma linha por conta cloud — a mesma conta
    Azure/AWS/GCP aparece repetida, uma vez por tipo de integração configurada.
    Deriva uma chave (provedor, identificador da conta) para deduplicar."""
    type_ = account.get("type") or ""
    data = account.get("data") or {}
    if type_.startswith("Azure"):
        return ("Azure", data.get("tenantId") or account.get("intgGuid"))
    if type_.startswith("Aws") or type_.startswith("AWS"):
        role_arn = (data.get("crossAccountCredentials") or {}).get("roleArn")
        return ("AWS", data.get("awsAccountId") or data.get("accountId") or role_arn or account.get("intgGuid"))
    if type_.startswith("Gcp") or type_.startswith("GCP"):
        cred = data.get("credentials") or {}
        return ("GCP", cred.get("clientEmail") or data.get("projectId") or account.get("intgGuid"))
    return (type_ or "Outro", account.get("intgGuid"))


def coverage_summary(machines_df, visibility_counts, cloud_accounts):
    machines_by_os = (
        machines_df.groupby("os").size().reset_index(name="count").sort_values("count", ascending=False)
        if machines_df is not None and not machines_df.empty
        else pd.DataFrame(columns=["os", "count"])
    )
    accounts = cloud_accounts or []
    healthy = [a for a in accounts if (a.get("state") or {}).get("ok")]
    unique_accounts = {_cloud_account_key(a) for a in accounts}
    unique_healthy = {_cloud_account_key(a) for a in healthy}
    return {
        "hosts_total": len(machines_df) if machines_df is not None else 0,
        "machines_by_os": machines_by_os,
        "visibility_counts": visibility_counts or {},
        "cloud_accounts_total": len(unique_accounts),
        "cloud_accounts_healthy": len(unique_healthy),
        "cloud_integrations_total": len(accounts),
        "cloud_accounts": accounts,
    }
