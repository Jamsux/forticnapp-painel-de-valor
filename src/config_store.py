"""Resolução e persistência local das credenciais da API do FortiCNAPP.

Ordem de prioridade:
1. Variáveis de ambiente (FORTICNAPP_KEY_ID / FORTICNAPP_SECRET / FORTICNAPP_ACCOUNT) —
   uso recomendado em Docker/produção.
2. Arquivo salvo em config/credentials.json — gerado pela página "Configuração" do dashboard.
3. Arquivo legado: qualquer .json na raiz do projeto contendo keyId/secret/account
   (mantido só por compatibilidade com o fluxo original de desenvolvimento).

Nada aqui sai da máquina do usuário — é só leitura/escrita de arquivo local.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT, "config")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")

REQUIRED_KEYS = ("keyId", "secret", "account")

ENV_MAP = {
    "keyId": "FORTICNAPP_KEY_ID",
    "secret": "FORTICNAPP_SECRET",
    "account": "FORTICNAPP_ACCOUNT",
}


class CredentialsNotConfigured(Exception):
    pass


def _valid(data):
    return isinstance(data, dict) and all(data.get(k) for k in REQUIRED_KEYS)


def from_env():
    creds = {k: os.environ.get(env_name, "") for k, env_name in ENV_MAP.items()}
    return creds if _valid(creds) else None


def load_saved():
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    try:
        with open(CREDENTIALS_PATH) as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None
    return data if _valid(data) else None


def _legacy_root_file():
    for path in glob.glob(os.path.join(ROOT, "*.json")):
        try:
            with open(path) as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue
        if _valid(data):
            return data
    return None


def resolve():
    """Retorna (credenciais, origem) ou (None, None) se nada estiver configurado."""
    creds = from_env()
    if creds:
        return creds, "env"
    creds = load_saved()
    if creds:
        return creds, "config_file"
    creds = _legacy_root_file()
    if creds:
        return creds, "legacy_root_file"
    return None, None


def save(key_id, secret, account):
    if not (key_id and secret and account):
        raise ValueError("keyId, secret e account são obrigatórios.")
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CREDENTIALS_PATH, "w") as fh:
        json.dump({"keyId": key_id, "secret": secret, "account": account}, fh, indent=2)
    try:
        os.chmod(CREDENTIALS_PATH, 0o600)
    except OSError:
        pass  # alguns sistemas de arquivo (ex: montagens Docker no Windows) não suportam chmod


def clear_saved():
    if os.path.exists(CREDENTIALS_PATH):
        os.remove(CREDENTIALS_PATH)
