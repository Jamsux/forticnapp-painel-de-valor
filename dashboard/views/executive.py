import plotly.graph_objects as go
import streamlit as st
from common import (sidebar_refresh_control, sidebar_period_selector, get_data, has_data,
                    num, SEVERITY_COLOR_MAP, PALETTE)
from src import aggregate
from src.glossary import help_text, label as gl
from src.i18n import t
from src.theme import category_label, severity_label

sidebar_refresh_control()
st.title(t("exec.title"))
st.caption(t("exec.caption"))

if not has_data():
    st.warning(t("report.no_data"))
    st.stop()

period = sidebar_period_selector()
data = get_data()
alerts_all = data["alerts"]
alerts_df = aggregate.filter_by_period(alerts_all, period["start"], period["end"])
vuln_df = data["vulns_critical_high"]
vuln_counts = data["vuln_severity_counts"]

akpi = aggregate.alert_headline_kpis(alerts_df)
pop = aggregate.period_over_period(alerts_all, period["start"], period["end"])
vkpi = aggregate.vuln_kpis(vuln_counts, vuln_df)
cov = aggregate.coverage_summary(data["machines"], data["visibility_counts"], data["cloud_accounts"])

if alerts_df is None or alerts_df.empty:
    st.warning(t("exec.no_alerts_in_period", period=period["label"]))
    st.stop()

# ---- Headline story ---------------------------------------------------
st.markdown(t("exec.headline", period=period["label"], total=num(akpi["total"]),
               open_pct=akpi["open_pct"], open=num(akpi["open"]), age=akpi["avg_open_age_days"]))

st.divider()

# ---- KPI row ------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    t("doc.kpi.alerts_period"), num(akpi["total"]),
    delta=(f"{'+' if pop['delta'] >= 0 else '-'}{num(abs(pop['delta']))} "
           f"{t('exec.vs_previous')}") if pop["delta"] is not None else None,
    help=help_text("alerts_total"),
)
c2.metric(gl("alerts_open_pct"), f"{akpi['open_pct']}%", help=help_text("alerts_open_pct"))
c3.metric(gl("alerts_critical_high_open"), akpi["critical_high_open"],
          help=help_text("alerts_critical_high_open"))
c4.metric(gl("alerts_avg_age"), f"{akpi['avg_open_age_days']} {t('unit.days')}",
          help=help_text("alerts_avg_age"))

st.markdown(t("exec.snapshot_row"))
c6, c7, c8, c9, c10 = st.columns(5)
c6.metric(gl("vulns_critical_high"), num(vkpi["critical_high_active"]),
          help=help_text("vulns_critical_high"))
c7.metric(gl("vulns_known_exploited"), num(vkpi["known_exploited"]),
          help=help_text("vulns_known_exploited"))
c8.metric(gl("vulns_malware"), num(vkpi["malware_associated"]), help=help_text("vulns_malware"))
c9.metric(gl("coverage_hosts"), cov["hosts_total"], help=help_text("coverage_hosts"))
c10.metric(gl("coverage_cloud_accounts"), cov["cloud_accounts_total"],
           help=help_text("coverage_cloud_accounts")
                + t("exec.here", value=t("doc.kpi.integrations",
                                          n=cov["cloud_integrations_total"])))

st.divider()

# ---- Trend --------------------------------------------------------------
st.subheader(t("exec.trend_title"), help=t("exec.trend_help"))
trend = aggregate.alerts_weekly_trend(alerts_df)
if not trend.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["week"], y=trend["total"], name="Total", mode="lines+markers",
                              line=dict(color=PALETTE["accent"])))
    fig.add_trace(go.Scatter(x=trend["week"], y=trend["critical_high"], name=f'{severity_label("Critical")}/{severity_label("High")}',
                              mode="lines+markers", line=dict(color=PALETTE["critical"])))
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10),
                       legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(t("exec.trend_empty"))

# ---- Tempo de resposta (MTTR) -------------------------------------------
st.subheader(t("exec.response_title"), help=t("exec.response_help"))
rkpi = aggregate.resolution_time_kpis(alerts_df)
bias = aggregate.response_bias_note(period["days"], rkpi["sample_size"])
if bias:
    st.warning(bias)

sem_amostra = rkpi["sample_size"] == 0
r1, r2, r3 = st.columns(3)
r1.metric(gl("mttr_median"), "—" if sem_amostra else f"{rkpi['mttr_days_median']} {t('unit.days')}",
          help=help_text("mttr_median") + t("exec.mttr_sample", n=num(rkpi["sample_size"])))
r2.metric(gl("mttr_p90"), "—" if sem_amostra else f"{rkpi['mttr_days_p90']} {t('unit.days')}",
          help=help_text("mttr_p90"))
r3.metric(gl("open_never_touched"), f"{rkpi['open_never_touched_pct']}%",
          help=help_text("open_never_touched")
               + t("exec.here", value=t("doc.kpi.of_total", part=num(rkpi["open_never_touched"]),
                                         total=num(rkpi["open_total"]))))

mttr_sev = aggregate.mttr_by_severity(alerts_df)
if not mttr_sev.empty:
    st.caption(f"**{gl('mttr_by_severity')}** — {help_text('mttr_by_severity')}")
    fig = go.Figure(go.Bar(
        x=[severity_label(s) for s in mttr_sev["severity"]], y=mttr_sev["mttr_days"],
        marker_color=[SEVERITY_COLOR_MAP.get(s, "#888") for s in mttr_sev["severity"]],
    ))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis_title=t("doc.col.mttr_days"))
    st.plotly_chart(fig, use_container_width=True)

with st.expander(t("exec.how_to_read")):
    st.markdown(t("exec.how_to_read_body"))

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader(gl("alerts_by_category"), help=help_text("alerts_by_category"))
    cat = aggregate.alerts_by_category(alerts_df)
    if not cat.empty:
        fig = go.Figure(go.Pie(labels=[category_label(c) for c in cat["category"]],
                                values=cat["count"], hole=0.45))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.caption(t("exec.category_caption"))

with col_b:
    st.subheader(gl("vulns_by_severity"), help=help_text("vulns_by_severity"))
    counts = vkpi["counts"]
    if counts:
        order = [s for s in aggregate.SEVERITY_ORDER if s in counts]
        fig = go.Figure(go.Bar(
            x=[severity_label(s) for s in order], y=[counts[s] for s in order],
            marker_color=[SEVERITY_COLOR_MAP.get(s, "#888") for s in order],
        ))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.caption(t("exec.vuln_caption", fixable=num(vkpi["fixable_now"]),
                 exploited=num(vkpi["known_exploited"]), wormable=num(vkpi["wormable"])))

st.divider()

# ---- Coverage / value visibility ----------------------------------------
st.subheader(t("exec.coverage_title"), help=t("exec.coverage_help"))
vc = cov["visibility_counts"]
if vc:
    chaves = {
        "hosts": "coverage_hosts", "containers": "coverage_containers", "users_os": "coverage_users",
        "applications": "coverage_applications",
        "network_interfaces": "coverage_network_interfaces", "packages": "coverage_packages",
    }
    cols = st.columns(len(vc))
    for col, (key, val) in zip(cols, vc.items()):
        col.metric(gl(chaves[key]) if key in chaves else key, num(val),
                    help=help_text(chaves[key]) if key in chaves else None)
    st.caption(t("exec.coverage_caption"))

contract_items = [
    (item.get("objName"), (item.get("props") or {}).get("numPurchased"),
     (item.get("props") or {}).get("numUsed"))
    for item in (data.get("contract_info") or [])
]
meaningful = [(name, p, u) for name, p, u in contract_items if p]
if meaningful:
    st.subheader(t("exec.contract_title"), help=t("exec.contract_help"))
    for name, purchased, used in meaningful:
        st.write(t("exec.contract_line", name=name, used=used if used is not None else 0,
                    purchased=purchased))
