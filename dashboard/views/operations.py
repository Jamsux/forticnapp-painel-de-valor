import plotly.graph_objects as go
import streamlit as st
from common import (sidebar_refresh_control, sidebar_period_selector, get_data, has_data,
                    num, PALETTE)
from src import aggregate
from src.glossary import alert_type_label, help_text, label as gl
from src.i18n import t

sidebar_refresh_control()
st.title(t("ops.title"))
st.caption(t("ops.caption"))

if not has_data():
    st.warning(t("report.no_data"))
    st.stop()

period = sidebar_period_selector()
data = get_data()
alerts_df = aggregate.filter_by_period(data["alerts"], period["start"], period["end"])
vuln_df = data["vulns_critical_high"]

st.subheader(t("ops.types_title", period=period["label"]), help=help_text("top_alert_types"))
top_types = aggregate.top_alert_types(alerts_df, n=12)
if not top_types.empty:
    # o nome técnico fica no hover: o analista usa para buscar no console do FortiCNAPP
    fig = go.Figure(go.Bar(
        x=top_types["count"],
        y=[alert_type_label(x) for x in top_types["alertType"]],
        orientation="h", marker_color=PALETTE["accent"],
        customdata=top_types["alertType"],
        hovertemplate=f"%{{y}}<br>{t('ops.hover_type')}: %{{customdata}}<br>"
                      f"{t('ops.hover_count')}: %{{x}}<extra></extra>",
    ))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader(gl("top_vulnerable_hosts"), help=help_text("top_vulnerable_hosts"))
    top_hosts = aggregate.top_vulnerable_hosts(vuln_df, n=10)
    if not top_hosts.empty:
        st.dataframe(top_hosts, use_container_width=True, hide_index=True)
    else:
        st.info(t("ops.top_hosts_empty"))

with col_b:
    st.subheader(gl("cloud_health"), help=help_text("cloud_health"))
    accounts = data.get("cloud_accounts") or []
    if accounts:
        rows = [
            {
                t("ops.cloud_col_name"): a.get("name"),
                t("ops.cloud_col_status"): t("ops.cloud_ok") if (a.get("state") or {}).get("ok")
                                            else t("ops.cloud_fail"),
                t("ops.cloud_col_last"): (a.get("state") or {}).get("lastSuccessfulTime"),
            }
            for a in accounts
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info(t("ops.cloud_empty"))

st.divider()

st.subheader(t("ops.known_exploited_title"), help=help_text("vulns_known_exploited"))
known = aggregate.known_exploited_table(vuln_df, n=30)
if not known.empty:
    st.dataframe(known, use_container_width=True, hide_index=True)
else:
    st.info(t("ops.known_exploited_empty"))

st.divider()

st.subheader(gl("open_alerts_table"), help=help_text("open_alerts_table"))
severities = ["Critical", "High", "Medium", "Low", "Info"]
selected = st.multiselect(t("ops.filter_severity"), severities, default=["Critical", "High"])
open_df = aggregate.open_alerts_table(alerts_df)
if not open_df.empty:
    filtered = open_df[open_df["severity"].isin(selected)] if selected else open_df
    st.caption(t("ops.open_alerts_count", shown=num(len(filtered)), total=num(len(open_df))))
    st.dataframe(filtered, use_container_width=True, hide_index=True)
else:
    st.info(t("ops.open_alerts_empty"))
