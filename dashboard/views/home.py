import streamlit as st
from common import sidebar_refresh_control, has_data, has_credentials
from src.i18n import t

sidebar_refresh_control()

st.title(t("home.title"))
st.markdown(t("home.intro"))

if not has_credentials():
    st.warning(t("home.need_credentials"))
elif not has_data():
    st.warning(t("home.need_data"))
else:
    st.info(t("home.ready"))
