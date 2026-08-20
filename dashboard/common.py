"""Utilidades compartilhadas pelas páginas do dashboard: idioma, dados e período."""
import datetime as dt
import os
import sys
import subprocess
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src import cache, aggregate, anonymize, config_store, i18n  # noqa: E402
from src.i18n import t  # noqa: E402
from src.theme import PALETTE, SEVERITY_COLOR_MAP  # noqa: E402,F401


# ------------------------------------------------------------------ idioma --

def apply_language():
    """Aplica o idioma guardado na sessão. Chamado no início de cada execução,
    antes de qualquer texto ser renderizado."""
    i18n.set_language(st.session_state.get("idioma", i18n.get_language()))


def sidebar_language_selector():
    """Seletor de idioma. Fica no topo da barra lateral porque muda tudo o que
    vem depois — inclusive os nomes das páginas no menu."""
    atual = st.session_state.get("idioma", i18n.get_language())
    with st.sidebar:
        escolhido = st.radio(
            t("sidebar.language"),
            i18n.SUPPORTED,
            index=i18n.SUPPORTED.index(atual) if atual in i18n.SUPPORTED else 0,
            format_func=lambda code: i18n.LANG_NAMES[code],
            horizontal=True,
            key="seletor_idioma",
        )
    if escolhido != atual:
        st.session_state["idioma"] = escolhido
        i18n.set_language(escolhido)
        st.rerun()
    st.session_state["idioma"] = escolhido
    i18n.set_language(escolhido)


# ------------------------------------------------------------------- dados --

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
    return load_all(st.session_state.get("cache_bust", 0))


def has_data():
    return cache.load_json("_refresh_meta") is not None


def has_credentials():
    creds, _source = config_store.resolve()
    return creds is not None


def run_refresh(alert_days=90, vuln_lookback_days=1):
    script = os.path.join(ROOT, "scripts", "refresh_data.py")
    proc = subprocess.run(
        [sys.executable, script, "--alert-days", str(alert_days),
         "--vuln-lookback-days", str(vuln_lookback_days)],
        cwd=ROOT, capture_output=True, text=True,
    )
    return proc.returncode == 0, proc.stdout + "\n" + proc.stderr


def sidebar_refresh_control():
    with st.sidebar:
        st.markdown(f"### {t('sidebar.local_data')}")
        if not has_credentials():
            st.warning(t("sidebar.no_credentials"))
            return
        meta = cache.load_json("_refresh_meta")
        st.caption(t("sidebar.last_updated", when=meta.get("refreshed_at", "?")) if meta
                   else t("sidebar.no_data_yet"))
        if st.button(t("sidebar.refresh_button"), use_container_width=True):
            with st.spinner(t("sidebar.refreshing")):
                ok, log = run_refresh()
            if ok:
                st.session_state["cache_bust"] = st.session_state.get("cache_bust", 0) + 1
                st.success(t("sidebar.refresh_ok"))
                st.rerun()
            else:
                st.error(t("sidebar.refresh_fail"))
                st.code(log)


# ----------------------------------------------------------------- período --

def period_presets():
    return {t("period.last_7"): 7, t("period.last_30"): 30, t("period.last_90"): 90}


def sidebar_period_selector():
    """Seletor de período compartilhado entre as páginas.

    Recorta apenas os indicadores de alertas — vulnerabilidades e inventário são
    a fotografia do momento da coleta, não uma série histórica. A API do
    FortiCNAPP guarda 90 dias, então esse é o limite do que se pode olhar.
    """
    alerts_df = get_data().get("alerts")
    data_min = alerts_df["startTime"].min() if alerts_df is not None and not alerts_df.empty else None
    data_max = alerts_df["startTime"].max() if alerts_df is not None and not alerts_df.empty else None
    now = pd.Timestamp(dt.datetime.now(dt.timezone.utc))
    presets = period_presets()

    with st.sidebar:
        st.markdown(f"### {t('sidebar.period')}")
        # O Streamlit descarta o estado de um widget quando ele deixa de ser
        # renderizado; o valor é espelhado numa chave própria de session_state
        # (não ligada a widget), que sobrevive à navegação entre páginas.
        opcoes = list(presets) + [t("period.custom")]
        indice_salvo = st.session_state.get("periodo_indice", 2)
        escolha = st.radio(
            t("sidebar.period_label"), opcoes,
            index=min(indice_salvo, len(opcoes) - 1),
            label_visibility="collapsed", key="period_preset",
        )
        st.session_state["periodo_indice"] = opcoes.index(escolha)

        if escolha == t("period.custom"):
            limite_min = data_min.date() if data_min is not None else (now - pd.Timedelta(days=90)).date()
            padrao = st.session_state.get(
                "periodo_intervalo", ((now - pd.Timedelta(days=30)).date(), now.date()))
            intervalo = st.date_input(
                t("period.range"), value=padrao, min_value=limite_min, max_value=now.date(),
                format="DD/MM/YYYY", key="period_custom_range",
            )
            if isinstance(intervalo, (tuple, list)) and len(intervalo) == 2:
                st.session_state["periodo_intervalo"] = tuple(intervalo)
                start = pd.Timestamp(intervalo[0], tz="UTC")
                end = pd.Timestamp(intervalo[1], tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            else:  # o usuário ainda está escolhendo a segunda data
                start = pd.Timestamp(
                    intervalo[0] if isinstance(intervalo, (tuple, list)) else intervalo, tz="UTC")
                end = now
            label = f"{start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}"
        else:
            dias = presets[escolha]
            start, end = now - pd.Timedelta(days=dias), now
            label = escolha.lower()

        if data_min is not None and start < data_min:
            st.caption(t("period.data_starts", date=data_min.strftime("%d/%m/%Y"),
                         days=aggregate.RETENTION_DAYS))
        st.caption(t("period.scope_note",
                     when=f" ({data_max.strftime('%d/%m/%Y')})" if data_max is not None else ""))

    return {"start": start, "end": end, "label": label, "days": max(1, (end - start).days)}


def filtered_alerts(period):
    """Alertas já recortados pelo período selecionado."""
    return aggregate.filter_by_period(get_data().get("alerts"), period["start"], period["end"])


def num(valor):
    """Separador de milhar conforme o idioma."""
    formatado = f"{valor:,}"
    return formatado if i18n.get_language() == "en" else formatado.replace(",", ".")
