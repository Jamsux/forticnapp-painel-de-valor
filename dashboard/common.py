"""Utilidades compartilhadas pelas páginas do dashboard: carregamento de dados cacheados."""
import datetime as dt
import os
import sys
import subprocess
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src import cache, aggregate, anonymize, config_store  # noqa: E402
from src.theme import PALETTE, SEVERITY_COLOR_MAP  # noqa: E402,F401


@st.cache_data(show_spinner=False)
def load_all(_cache_bust=0):
    # anonymize_data devolve os dados intactos fora do modo demo
    return anonymize.anonymize_data({
        "alerts": cache.load_df("alerts"),
        "vuln_severity_counts": cache.load_json("vuln_severity_counts"),
        "vulns_critical_high": cache.load_df("vulns_critical_high"),
        "machines": cache.load_df("machines"),
        "visibility_counts": cache.load_json("visibility_counts"),
        "cloud_accounts": cache.load_json("cloud_accounts"),
        "contract_info": cache.load_json("contract_info"),
        "alert_rules": cache.load_json("alert_rules"),
        "report_rules": cache.load_json("report_rules"),
        "resource_groups": cache.load_json("resource_groups"),
        "refresh_meta": cache.load_json("_refresh_meta"),
    })


def get_data():
    bust = st.session_state.get("cache_bust", 0)
    return load_all(bust)


def has_data():
    meta = cache.load_json("_refresh_meta")
    return meta is not None


def has_credentials():
    creds, _source = config_store.resolve()
    return creds is not None


def run_refresh(alert_days=90, vuln_lookback_days=1):
    script = os.path.join(ROOT, "scripts", "refresh_data.py")
    python_bin = sys.executable
    proc = subprocess.run(
        [python_bin, script, "--alert-days", str(alert_days), "--vuln-lookback-days", str(vuln_lookback_days)],
        cwd=ROOT, capture_output=True, text=True,
    )
    return proc.returncode == 0, proc.stdout + "\n" + proc.stderr


def sidebar_refresh_control():
    with st.sidebar:
        st.markdown("### Dados locais")
        if not has_credentials():
            st.warning("Credenciais não configuradas.")
            st.page_link("pages/0_⚙️_Configuração.py", label="Ir para Configuração", icon="⚙️")
            return
        meta = cache.load_json("_refresh_meta")
        if meta:
            st.caption(f"Última atualização: {meta.get('refreshed_at', '?')}")
        else:
            st.caption("Nenhum dado coletado ainda.")
        if st.button("🔄 Atualizar dados do FortiCNAPP", use_container_width=True):
            with st.spinner("Consultando a API do FortiCNAPP... isso pode levar 1-2 minutos."):
                ok, log = run_refresh()
            if ok:
                st.session_state["cache_bust"] = st.session_state.get("cache_bust", 0) + 1
                st.success("Dados atualizados.")
                st.rerun()
            else:
                st.error("Falha ao atualizar. Veja detalhes abaixo.")
                st.code(log)


PERIOD_PRESETS = {
    "Últimos 7 dias": 7,
    "Últimos 30 dias": 30,
    "Últimos 90 dias": 90,
}


def sidebar_period_selector():
    """Seletor de período compartilhado entre as páginas.

    Recorta apenas os indicadores de alertas — vulnerabilidades e inventário são
    a fotografia do momento da coleta, não uma série histórica. A API do
    FortiCNAPP guarda 90 dias, então esse é o limite do que se pode olhar.

    Devolve dict com start, end, label e days.
    """
    alerts_df = get_data().get("alerts")
    data_min = alerts_df["startTime"].min() if alerts_df is not None and not alerts_df.empty else None
    data_max = alerts_df["startTime"].max() if alerts_df is not None and not alerts_df.empty else None
    now = pd.Timestamp(dt.datetime.now(dt.timezone.utc))

    with st.sidebar:
        st.markdown("### Período")
        # O Streamlit descarta o estado de um widget quando ele deixa de ser
        # renderizado — ao trocar de página, a escolha se perderia. Por isso o valor
        # é espelhado numa chave comum de session_state (não ligada a widget), que
        # sobrevive à navegação e realimenta o widget na página seguinte.
        opcoes = list(PERIOD_PRESETS) + ["Personalizado"]
        salvo = st.session_state.get("periodo_escolhido", "Últimos 90 dias")
        escolha = st.radio(
            "Período analisado", opcoes,
            index=opcoes.index(salvo) if salvo in opcoes else 2,
            label_visibility="collapsed", key="period_preset",
        )
        st.session_state["periodo_escolhido"] = escolha

        if escolha == "Personalizado":
            limite_min = data_min.date() if data_min is not None else (now - pd.Timedelta(days=90)).date()
            padrao = st.session_state.get(
                "periodo_intervalo", ((now - pd.Timedelta(days=30)).date(), now.date())
            )
            intervalo = st.date_input(
                "Intervalo",
                value=padrao,
                min_value=limite_min,
                max_value=now.date(),
                format="DD/MM/YYYY",
                key="period_custom_range",
            )
            if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
                st.session_state["periodo_intervalo"] = tuple(intervalo)
            if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
                start = pd.Timestamp(intervalo[0], tz="UTC")
                end = pd.Timestamp(intervalo[1], tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            else:  # o usuário ainda está escolhendo a segunda data
                start = pd.Timestamp(intervalo[0] if isinstance(intervalo, (tuple, list)) else intervalo, tz="UTC")
                end = now
            label = f"{start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}"
        else:
            dias = PERIOD_PRESETS[escolha]
            start, end = now - pd.Timedelta(days=dias), now
            label = escolha.lower()

        if data_min is not None and start < data_min:
            st.caption(
                f"⚠️ Há dados a partir de {data_min.strftime('%d/%m/%Y')} "
                f"(a API mantém {aggregate.RETENTION_DAYS} dias)."
            )
        st.caption(f"Recorta os indicadores de **alertas**. Vulnerabilidades e cobertura "
                   f"refletem a coleta mais recente"
                   + (f" ({data_max.strftime('%d/%m/%Y')})." if data_max is not None else "."))

    return {"start": start, "end": end, "label": label, "days": max(1, (end - start).days)}


def filtered_alerts(period):
    """Alertas já recortados pelo período selecionado."""
    return aggregate.filter_by_period(get_data().get("alerts"), period["start"], period["end"])
