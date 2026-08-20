"""Ponto de entrada do painel.

Usa st.navigation em vez da descoberta automática da pasta pages/: assim os nomes
das páginas no menu também acompanham o idioma escolhido, o que a descoberta
automática não permite (ela usa o nome do arquivo, que é fixo).
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import apply_language, sidebar_language_selector  # noqa: E402
from src.i18n import t  # noqa: E402

st.set_page_config(page_title="FortiCNAPP — Value Dashboard", page_icon="🛡️", layout="wide")

# o idioma precisa ser resolvido antes de qualquer texto — inclusive o menu
apply_language()
sidebar_language_selector()

paginas = [
    st.Page("views/home.py", title=t("page.home"), icon="🏠", default=True),
    st.Page("views/settings.py", title=t("page.settings"), icon="⚙️"),
    st.Page("views/executive.py", title=t("page.executive"), icon="📊"),
    st.Page("views/operations.py", title=t("page.operations"), icon="🛠️"),
    st.Page("views/report.py", title=t("page.report"), icon="🖨️"),
]

st.navigation(paginas).run()
