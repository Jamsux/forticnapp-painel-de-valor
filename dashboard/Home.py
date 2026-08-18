import streamlit as st
from common import sidebar_refresh_control, has_data, has_credentials

st.set_page_config(page_title="FortiCNAPP — Painel de Valor", page_icon="🛡️", layout="wide")

sidebar_refresh_control()

st.title("🛡️ FortiCNAPP — Painel de Valor")
st.markdown(
    """
Este painel conecta diretamente à API do FortiCNAPP da sua conta e traduz os dados brutos
em indicadores para dois públicos:

- **Visão Gerencial** — indicadores para o decisor de segurança/tecnologia.
- **Operações de Segurança** — indicadores acionáveis para o time técnico.

Os dados ficam **armazenados localmente** (pasta `data/`) e só saem da sua máquina para consultar
a própria API do FortiCNAPP.
"""
)

if not has_credentials():
    st.warning("Antes de começar, cadastre sua API Key do FortiCNAPP.")
    st.page_link("pages/0_⚙️_Configuração.py", label="Ir para Configuração", icon="⚙️")
elif not has_data():
    st.warning("Credenciais configuradas. Agora use **Atualizar dados** na barra lateral para a primeira coleta.")
else:
    st.info("Dados carregados. Use o menu à esquerda para navegar entre os dashboards.")
