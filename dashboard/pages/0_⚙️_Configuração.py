import streamlit as st
from common import ROOT  # noqa: F401  (garante sys.path configurado)
from src import config_store
from src.forticnapp_client import test_connection

st.set_page_config(page_title="Configuração — FortiCNAPP", page_icon="⚙️", layout="wide")
st.title("⚙️ Configuração")
st.caption("Cadastre a API Key do FortiCNAPP para conectar este painel à sua conta.")

creds, source = config_store.resolve()

SOURCE_LABELS = {
    "env": "variáveis de ambiente (definidas na implantação)",
    "config_file": "arquivo salvo localmente por esta tela",
    "legacy_root_file": "arquivo de credenciais solto na raiz do projeto",
}

if creds:
    masked_key = creds["keyId"][:6] + "…" if len(creds["keyId"]) > 6 else creds["keyId"]
    st.success(
        f"Credenciais ativas — origem: **{SOURCE_LABELS.get(source, source)}**. "
        f"Conta: `{creds['account']}` · Key ID: `{masked_key}`"
    )
else:
    st.warning("Nenhuma credencial configurada ainda. Preencha o formulário abaixo.")

if source == "env":
    st.info(
        "As credenciais atuais vêm de variáveis de ambiente (`FORTICNAPP_KEY_ID`, "
        "`FORTICNAPP_SECRET`, `FORTICNAPP_ACCOUNT`) e têm prioridade sobre o que for "
        "salvo aqui. Para usar esta tela, remova essas variáveis da implantação."
    )

st.divider()

with st.expander("Onde encontro esses dados?", expanded=not creds):
    st.markdown(
        """
1. Acesse o console do FortiCNAPP (URL no formato `https://SUACONTA.lacework.net`).
2. Vá em **Settings → API Keys** e crie uma chave com permissão de leitura.
3. Baixe o arquivo `.json` gerado — ele contém `keyId`, `secret` e `account`.
   Você pode colar o conteúdo inteiro abaixo, ou preencher os três campos manualmente.
"""
    )

paste_mode = st.toggle("Colar o JSON da chave de uma vez", value=False)

key_id = secret = account = ""

if paste_mode:
    raw = st.text_area(
        "Cole aqui o conteúdo do arquivo .json da API Key",
        height=140,
        placeholder='{\n  "keyId": "...",\n  "secret": "...",\n  "account": "suaconta.lacework.net"\n}',
    )
    if raw.strip():
        import json
        try:
            parsed = json.loads(raw)
            key_id = parsed.get("keyId", "")
            secret = parsed.get("secret", "")
            account = parsed.get("account", "")
            if not (key_id and secret and account):
                st.error("O JSON precisa conter keyId, secret e account.")
        except json.JSONDecodeError:
            st.error("JSON inválido — confira se colou o arquivo completo.")
else:
    account = st.text_input("Account", placeholder="suaconta.lacework.net",
                             value=creds["account"] if creds and source == "config_file" else "")
    key_id = st.text_input("Key ID", placeholder="123456_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                            value=creds["keyId"] if creds and source == "config_file" else "")
    secret = st.text_input("Secret", type="password", placeholder="••••••••••••••••••••••••••••••••")

col1, col2, col3 = st.columns([1, 1, 2])
test_clicked = col1.button("Testar conexão")
save_clicked = col2.button("💾 Salvar", type="primary")

if test_clicked or save_clicked:
    if not (key_id and secret and account):
        st.error("Preencha Account, Key ID e Secret antes de continuar.")
    else:
        with st.spinner("Autenticando no FortiCNAPP..."):
            ok, message = test_connection(key_id, secret, account)
        if ok:
            st.success(message)
            if save_clicked:
                account_clean = account.strip()
                if "://" in account_clean:
                    account_clean = account_clean.split("://", 1)[1]
                account_clean = account_clean.strip("/")
                config_store.save(key_id.strip(), secret.strip(), account_clean)
                st.success("Credenciais salvas em `config/credentials.json` (fora do repositório/imagem).")
                st.session_state["cache_bust"] = st.session_state.get("cache_bust", 0) + 1
                st.rerun()
        else:
            st.error(message)

if creds and source == "config_file":
    st.divider()
    with st.expander("Remover credenciais salvas"):
        st.warning("Isso apaga config/credentials.json. Os dados já coletados em data/ não são afetados.")
        if st.button("Remover credenciais salvas", type="secondary"):
            config_store.clear_saved()
            st.session_state["cache_bust"] = st.session_state.get("cache_bust", 0) + 1
            st.rerun()
