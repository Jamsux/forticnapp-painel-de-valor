import plotly.graph_objects as go
import streamlit as st
from common import (sidebar_refresh_control, sidebar_period_selector, get_data, has_data, PALETTE)
from src import aggregate
from src.glossary import alert_type_label, help_text

st.set_page_config(page_title="Operações de Segurança — FortiCNAPP", page_icon="🛠️", layout="wide")
sidebar_refresh_control()
st.title("🛠️ Operações de Segurança")
st.caption("Fila de trabalho: o que priorizar agora.")

if not has_data():
    st.warning("Nenhum dado coletado ainda. Use **Atualizar dados** na barra lateral.")
    st.stop()

period = sidebar_period_selector()
data = get_data()
alerts_df = aggregate.filter_by_period(data["alerts"], period["start"], period["end"])
vuln_df = data["vulns_critical_high"]

st.subheader(f"Tipos de alerta mais frequentes — {period['label']}",
             help=help_text("top_alert_types"))
top_types = aggregate.top_alert_types(alerts_df, n=12)
if not top_types.empty:
    # o nome técnico fica no hover: o analista usa para buscar no console do FortiCNAPP
    fig = go.Figure(go.Bar(
        x=top_types["count"],
        y=[alert_type_label(t) for t in top_types["alertType"]],
        orientation="h", marker_color=PALETTE["accent"],
        customdata=top_types["alertType"],
        hovertemplate="%{y}<br>tipo: %{customdata}<br>ocorrências: %{x}<extra></extra>",
    ))
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Servidores com mais vulnerabilidades", help=help_text("top_vulnerable_hosts"))
    top_hosts = aggregate.top_vulnerable_hosts(vuln_df, n=10)
    if not top_hosts.empty:
        st.dataframe(top_hosts, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados de vulnerabilidades.")

with col_b:
    st.subheader("Saúde das integrações cloud", help=help_text("cloud_health"))
    accounts = data.get("cloud_accounts") or []
    if accounts:
        rows = [
            {
                "Nome": a.get("name"),
                "Status": "OK" if (a.get("state") or {}).get("ok") else "⚠️ Falha",
                "Última coleta OK": (a.get("state") or {}).get("lastSuccessfulTime"),
            }
            for a in accounts
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma conta cloud cacheada.")

st.divider()

st.subheader("Vulnerabilidades com exploit conhecido (priorizar primeiro)",
             help=help_text("vulns_known_exploited"))
known = aggregate.known_exploited_table(vuln_df, n=30)
if not known.empty:
    st.dataframe(known, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma falha com ferramenta de ataque disponível ou uso confirmado por malware "
            "foi identificada na última coleta.")

st.divider()

st.subheader("Alertas em aberto", help=help_text("open_alerts_table"))
severities = ["Critical", "High", "Medium", "Low", "Info"]
selected = st.multiselect("Filtrar por severidade", severities, default=["Critical", "High"])
open_df = aggregate.open_alerts_table(alerts_df)
if not open_df.empty:
    filtered = open_df[open_df["severity"].isin(selected)] if selected else open_df
    st.caption(f"{len(filtered)} alertas em aberto (de {len(open_df)} no total).")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum alerta em aberto no período coletado.")
