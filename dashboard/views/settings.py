import json

import streamlit as st
from common import ROOT  # noqa: F401  (garante sys.path configurado)
from src import config_store
from src.forticnapp_client import test_connection
from src.i18n import t

st.title(t("settings.title"))
st.caption(t("settings.caption"))

creds, source = config_store.resolve()

if creds:
    masked_key = creds["keyId"][:6] + "…" if len(creds["keyId"]) > 6 else creds["keyId"]
    st.success(t("settings.active", source=t(f"settings.source.{source}"),
                 account=creds["account"], key=masked_key))
else:
    st.warning(t("settings.none"))

if source == "env":
    st.info(t("settings.env_notice"))

st.divider()

with st.expander(t("settings.where_expander"), expanded=not creds):
    st.markdown(t("settings.where_body"))

paste_mode = st.toggle(t("settings.paste_toggle"), value=False)

key_id = secret = account = ""

if paste_mode:
    raw = st.text_area(
        t("settings.paste_area"), height=140,
        placeholder='{\n  "keyId": "...",\n  "secret": "...",\n  "account": "youraccount.lacework.net"\n}',
    )
    if raw.strip():
        try:
            parsed = json.loads(raw)
            key_id = parsed.get("keyId", "")
            secret = parsed.get("secret", "")
            account = parsed.get("account", "")
            if not (key_id and secret and account):
                st.error(t("settings.json_needs_fields"))
        except json.JSONDecodeError:
            st.error(t("settings.json_invalid"))
else:
    account = st.text_input("Account", placeholder="youraccount.lacework.net",
                             value=creds["account"] if creds and source == "config_file" else "")
    key_id = st.text_input("Key ID", placeholder="123456_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                            value=creds["keyId"] if creds and source == "config_file" else "")
    secret = st.text_input("Secret", type="password", placeholder="••••••••••••••••••••••••••••••••")

col1, col2, _ = st.columns([1, 1, 2])
test_clicked = col1.button(t("settings.test"))
save_clicked = col2.button(t("settings.save"), type="primary")

if test_clicked or save_clicked:
    if not (key_id and secret and account):
        st.error(t("settings.fill_all"))
    else:
        with st.spinner(t("settings.testing")):
            ok, message = test_connection(key_id, secret, account)
        if ok:
            st.success(message)
            if save_clicked:
                account_clean = account.strip()
                if "://" in account_clean:
                    account_clean = account_clean.split("://", 1)[1]
                config_store.save(key_id.strip(), secret.strip(), account_clean.strip("/"))
                st.success(t("settings.saved"))
                st.session_state["cache_bust"] = st.session_state.get("cache_bust", 0) + 1
                st.rerun()
        else:
            st.error(message)

if creds and source == "config_file":
    st.divider()
    with st.expander(t("settings.remove_expander")):
        st.warning(t("settings.remove_warning"))
        if st.button(t("settings.remove_button"), type="secondary"):
            config_store.clear_saved()
            st.session_state["cache_bust"] = st.session_state.get("cache_bust", 0) + 1
            st.rerun()
