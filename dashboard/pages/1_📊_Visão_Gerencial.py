import plotly.graph_objects as go
import streamlit as st
from common import (sidebar_refresh_control, sidebar_period_selector, get_data, has_data,
                    SEVERITY_COLOR_MAP, PALETTE)
from src import aggregate
from src.glossary import help_text
from src.theme import category_label

st.set_page_config(page_title="Visão Gerencial — FortiCNAPP", page_icon="📊", layout="wide")
sidebar_refresh_control()
st.title("📊 Visão Gerencial")
st.caption("Indicadores para decisão: risco, tendência, backlog de resposta e utilização do produto.")

if not has_data():
    st.warning("Nenhum dado coletado ainda. Use **Atualizar dados** na barra lateral.")
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
    st.warning(f"Nenhum alerta no período selecionado ({period['label']}).")
    st.stop()

# ---- Headline story ---------------------------------------------------
if akpi["total"]:
    st.markdown(
        f"""
> #### No período analisado ({period['label']}), o FortiCNAPP gerou **{akpi['total']:,}** alertas —
> **{akpi['open_pct']}%** ({akpi['open']:,}) ainda estão **em aberto**, com idade média de
> **{akpi['avg_open_age_days']} dias**. O produto está detectando; o gargalo está na resposta.
""".replace(",", ".")
    )

st.divider()

# ---- KPI row ------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric(
    "Alertas no período", f"{akpi['total']:,}".replace(",", "."),
    delta=(f"{pop['delta']:+,}".replace(",", ".") + " vs. período anterior") if pop["delta"] is not None else None,
    help=help_text("alerts_total"),
)
c2.metric("% em aberto", f"{akpi['open_pct']}%", help=help_text("alerts_open_pct"))
c3.metric("Críticos/Altos em aberto", akpi["critical_high_open"],
          help=help_text("alerts_critical_high_open"))
c4.metric("Idade média (aberto)", f"{akpi['avg_open_age_days']} dias",
          help=help_text("alerts_avg_age"))

st.markdown("###### Posição atual — não muda com o período selecionado")
c6, c7, c8, c9, c10 = st.columns(5)
c6.metric("Vulnerabilidades críticas e altas", f"{vkpi['critical_high_active']:,}".replace(",", "."),
          help=help_text("vulns_critical_high"))
c7.metric("Com exploit conhecido", f"{vkpi['known_exploited']:,}".replace(",", "."),
          help=help_text("vulns_known_exploited"))
c8.metric("Associadas a malware/ransomware", f"{vkpi['malware_associated']:,}".replace(",", "."),
          help=help_text("vulns_malware"))
c9.metric("Servidores monitorados", cov["hosts_total"], help=help_text("coverage_hosts"))
c10.metric("Contas cloud monitoradas", cov["cloud_accounts_total"],
           help=help_text("coverage_cloud_accounts")
                + f" Nesta conta: {cov['cloud_integrations_total']} integrações configuradas.")

st.divider()

# ---- Trend --------------------------------------------------------------
st.subheader("Tendência semanal de alertas",
             help="Volume de alertas criados por semana, com a linha de Críticos/Altos "
                  "destacada. Mostra se a exposição está crescendo, estável ou caindo ao "
                  "longo do período — a leitura de tendência que um snapshot não dá.")
trend = aggregate.alerts_weekly_trend(alerts_df)
if not trend.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend["week"], y=trend["total"], name="Total", mode="lines+markers",
                              line=dict(color=PALETTE["accent"])))
    fig.add_trace(go.Scatter(x=trend["week"], y=trend["critical_high"], name="Críticos/Altos", mode="lines+markers",
                              line=dict(color=PALETTE["critical"])))
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem dados suficientes para tendência.")

# ---- Tempo de resposta (MTTR) -------------------------------------------
st.subheader(
    "Tempo de resposta",
    help="Quanto tempo o time leva para tratar o que o produto detecta. Mede a eficiência "
         "do processo de resposta — não a qualidade da detecção.",
)
rkpi = aggregate.resolution_time_kpis(alerts_df)
bias = aggregate.response_bias_note(period["days"], rkpi["sample_size"])
if bias:
    st.warning(bias)

sem_amostra = rkpi["sample_size"] == 0
r1, r2, r3 = st.columns(3)
r1.metric("MTTR (mediana)", "—" if sem_amostra else f"{rkpi['mttr_days_median']} dias",
          help=help_text("mttr_median")
               + f" Amostra: {rkpi['sample_size']:,} alertas fechados.".replace(",", "."))
r2.metric("MTTR (p90)", "—" if sem_amostra else f"{rkpi['mttr_days_p90']} dias",
          help=help_text("mttr_p90"))
r3.metric(
    "Alertas abertos sem qualquer interação",
    f"{rkpi['open_never_touched_pct']}%",
    help=help_text("open_never_touched")
         + f" Nesta conta: {rkpi['open_never_touched']:,} de {rkpi['open_total']:,}.".replace(",", "."),
)

mttr_sev = aggregate.mttr_by_severity(alerts_df)
if not mttr_sev.empty:
    st.caption(f"**MTTR por severidade** — {help_text('mttr_by_severity')}")
    fig = go.Figure(go.Bar(
        x=mttr_sev["severity"], y=mttr_sev["mttr_days"],
        marker_color=[SEVERITY_COLOR_MAP.get(s, "#888") for s in mttr_sev["severity"]],
    ))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="dias (mediana)")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Como ler estes números"):
    st.markdown(
        """
- **Tempo de resolução (MTTR)** — mede o intervalo entre a abertura de um alerta e o seu
  encerramento, considerando apenas os alertas já tratados. É apresentado como o **caso do meio**
  (mediana), e não como média, para que poucos casos extremos não distorçam a leitura.

- **Tempo até o primeiro atendimento (MTTA) não é apresentado** — e isso é uma limitação da
  ferramenta, não uma omissão. Ela registra apenas dois momentos: quando o alerta nasce e quando é
  encerrado. Não existe um registro de "alguém assumiu este alerta", então qualquer número aqui
  seria estimativa. No lugar, mostramos um dado verificável e mais direto: **quantos alertas seguem
  sem nenhum atendimento** desde que foram criados.

- **Tempo até a detecção (MTTD) também não é apresentado** — exigiria saber quando o problema
  realmente começou, e não apenas quando foi detectado. Esse instante não é registrado por nenhuma
  ferramenta desta categoria.
"""
    )

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Alertas por categoria", help=help_text("alerts_by_category"))
    cat = aggregate.alerts_by_category(alerts_df)
    if not cat.empty:
        fig = go.Figure(go.Pie(labels=[category_label(c) for c in cat["category"]],
                                values=cat["count"], hole=0.45))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "**Configuração** — erros de configuração no ambiente de nuvem. "
        "**Comportamento** e **Correlação** — atividade fora do padrão observada dentro dos "
        "servidores. Estes dois últimos são o tipo de detecção que os controles nativos dos "
        "provedores de nuvem normalmente não entregam."
    )

with col_b:
    st.subheader("Vulnerabilidades ativas por severidade", help=help_text("vulns_by_severity"))
    counts = vkpi["counts"]
    if counts:
        order = [s for s in aggregate.SEVERITY_ORDER if s in counts]
        fig = go.Figure(go.Bar(
            x=order, y=[counts[s] for s in order],
            marker_color=[SEVERITY_COLOR_MAP.get(s, "#888") for s in order],
        ))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    st.caption(
        f"**{vkpi['fixable_now']:,}** dessas falhas já têm atualização disponível do fabricante — "
        f"dependem apenas de aplicar a correção. **{vkpi['known_exploited']:,}** já possuem "
        f"ferramenta de ataque pronta e disponível, e **{vkpi['wormable']:,}** conseguem se "
        f"espalhar sozinhas entre servidores.".replace(",", ".")
    )

st.divider()

# ---- Coverage / value visibility ----------------------------------------
st.subheader(
    "Amplitude de visibilidade (o que o produto está observando)",
    help="Volume de entidades que o FortiCNAPP inventaria e monitora continuamente — "
         "visibilidade que normalmente exigiria múltiplas ferramentas nativas para "
         "reconstruir manualmente.",
)
vc = cov["visibility_counts"]
if vc:
    cols = st.columns(len(vc))
    labels = {
        "hosts": "Hosts", "containers": "Containers", "users_os": "Contas de usuário observadas",
        "applications": "Aplicações", "network_interfaces": "Interfaces de rede", "packages": "Pacotes de software",
    }
    help_keys = {
        "hosts": "coverage_hosts", "containers": "coverage_containers", "users_os": "coverage_users",
        "applications": "coverage_applications", "network_interfaces": "coverage_network_interfaces",
        "packages": "coverage_packages",
    }
    for col, (key, val) in zip(cols, vc.items()):
        col.metric(
            labels.get(key, key), f"{val:,}".replace(",", "."),
            help=help_text(help_keys[key]) if key in help_keys else None,
        )
    st.caption(
        "Inventário que o produto mantém atualizado sozinho, de forma contínua. Reconstruir esse "
        "mesmo mapa manualmente, ou com os controles nativos de cada provedor de nuvem, exigiria "
        "várias ferramentas e trabalho recorrente da equipe."
    )

contract_items = [
    (item.get("objName"), (item.get("props") or {}).get("numPurchased"), (item.get("props") or {}).get("numUsed"))
    for item in (data.get("contract_info") or [])
]
meaningful_contract_items = [(name, p, u) for name, p, u in contract_items if p]
if meaningful_contract_items:
    st.subheader(
        "Utilização do contrato",
        help="Quanto do que foi contratado está efetivamente em uso (ex.: licenças de agente "
             "usadas vs. adquiridas). Só é exibido quando a API retorna um total contratado "
             "válido para o item.",
    )
    for name, purchased, used in meaningful_contract_items:
        st.write(f"**{name}** — usados {used if used is not None else 0} de {purchased} contratados")
