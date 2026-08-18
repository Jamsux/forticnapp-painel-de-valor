"""Cliente mínimo para a API v2 do FortiCNAPP (Lacework)."""
import time
import datetime as dt
import requests

from . import config_store

TOKEN_TTL_SECONDS = 3300  # a API expira em 3600s, renovamos um pouco antes


class ForticnappClient:
    def __init__(self, credentials=None):
        if credentials is None:
            credentials, _source = config_store.resolve()
        if not credentials:
            raise config_store.CredentialsNotConfigured(
                "Nenhuma credencial do FortiCNAPP configurada. Use a página "
                "'Configuração' do dashboard, defina as variáveis de ambiente "
                "FORTICNAPP_KEY_ID/FORTICNAPP_SECRET/FORTICNAPP_ACCOUNT, ou rode "
                "scripts/refresh_data.py depois de configurar."
            )
        self.creds = credentials
        self.base_url = f"https://{self.creds['account']}"
        self._token = None
        self._token_expires_at = 0

    def _ensure_token(self):
        if self._token and time.time() < self._token_expires_at:
            return
        resp = requests.post(
            f"{self.base_url}/api/v2/access/tokens",
            headers={
                "Content-Type": "application/json",
                "X-LW-UAKS": self.creds["secret"],
            },
            json={"keyId": self.creds["keyId"], "expiryTime": 3600},
            timeout=30,
        )
        resp.raise_for_status()
        self._token = resp.json()["token"]
        self._token_expires_at = time.time() + TOKEN_TTL_SECONDS

    def _headers(self):
        self._ensure_token()
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def get(self, path, params=None):
        resp = requests.get(f"{self.base_url}{path}", headers=self._headers(), params=params, timeout=60)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"data": []}
        return resp.json()

    def post(self, path, body):
        resp = requests.post(f"{self.base_url}{path}", headers=self._headers(), json=body, timeout=60)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"data": []}
        return resp.json()

    def search_all_pages(self, path, body, max_pages=200):
        """POST em um endpoint /search e segue paging.urls.nextPage até o fim."""
        rows = []
        page = self.post(path, body)
        rows.extend(page.get("data", []))
        next_url = page.get("paging", {}).get("urls", {}).get("nextPage")
        pages_fetched = 1
        while next_url and pages_fetched < max_pages:
            resp = requests.get(next_url, headers=self._headers(), timeout=60)
            resp.raise_for_status()
            page = resp.json()
            rows.extend(page.get("data", []))
            next_url = page.get("paging", {}).get("urls", {}).get("nextPage")
            pages_fetched += 1
        return rows

    def search_time_windows(self, path, base_body, start, end, window_days=7, max_pages_per_window=200):
        """Alguns endpoints (ex: Alerts) limitam startTime..endTime a N dias.
        Faz o fatiamento e concatena os resultados de todas as janelas."""
        rows = []
        cursor = start
        while cursor < end:
            window_end = min(cursor + dt.timedelta(days=window_days), end)
            body = dict(base_body)
            body["timeFilter"] = {
                "startTime": cursor.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "endTime": window_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            rows.extend(self.search_all_pages(path, body, max_pages=max_pages_per_window))
            cursor = window_end
        return rows


def test_connection(key_id, secret, account):
    """Tenta autenticar com as credenciais informadas. Retorna (ok: bool, mensagem: str)."""
    account = account.strip()
    if "://" in account:
        account = account.split("://", 1)[1]
    account = account.strip("/")
    try:
        resp = requests.post(
            f"https://{account}/api/v2/access/tokens",
            headers={"Content-Type": "application/json", "X-LW-UAKS": secret},
            json={"keyId": key_id, "expiryTime": 60},
            timeout=15,
        )
    except requests.exceptions.RequestException as exc:
        return False, f"Não foi possível conectar em https://{account}: {exc}"
    if resp.status_code == 201:
        return True, "Conexão autenticada com sucesso."
    return False, f"Falha na autenticação (HTTP {resp.status_code}): {resp.text[:200]}"
