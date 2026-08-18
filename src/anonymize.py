"""Modo demonstração: mascara identificadores do cliente para capturas de tela e demos.

Ativado por variável de ambiente (FORTICNAPP_DEMO=1). Atua no carregamento dos
dados, de modo que dashboards, relatório e PDF ficam mascarados de uma vez — não
há caminho em que um nome real escape por ter sido esquecido numa tela.

O que é mascarado:
  - nomes de servidores (hostnames), inclusive quando citados dentro de textos livres
  - domínio Windows e contas de usuário no formato DOMINIO\\usuario
  - nomes das integrações/contas cloud
  - endereços de e-mail

O que NÃO é mascarado (não identifica o cliente e é o que dá sentido à demo):
  - nomes de alertas e de políticas (são catálogo do produto)
  - identificadores de CVE, severidades, contagens e datas
"""
import os
import re

DEMO_ENV_VAR = "FORTICNAPP_DEMO"

EMAIL_RE = re.compile(r"[\w.\-+]+@[\w.\-]+\.\w+")
DOMAIN_USER_RE = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9\-_]{1,}\\[^\s,;)]+")

# Alertas antigos citam servidores que já saíram do inventário, então a lista de
# hostnames conhecidos não basta. Estes padrões cobrem as formas como a API
# escreve nomes de máquina e de usuário nas descrições.
HOST_PHRASE_RE = re.compile(r"\b(on host|from host|host)\s+([A-Za-z0-9][\w.\-]{2,})", re.IGNORECASE)
HOSTS_LIST_RE = re.compile(r"\bHosts:\s*([^.]+)", re.IGNORECASE)
USER_PHRASE_RE = re.compile(r"\bas user\s+([^\s,;)]+)", re.IGNORECASE)
# Nomes tipo SRV-APP-PRD-01 (três ou mais segmentos), sem pegar CVE-2026-12345
DASHED_NAME_RE = re.compile(r"\b(?!CVE\b)[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+){2,}\b")

# Palavras genéricas nos nomes de integração que não identificam ninguém
_STOPWORDS = {
    "azure", "aws", "gcp", "cloud", "activity", "logs", "log", "audit", "config",
    "lacework", "forticnapp", "integration", "integracao", "account", "accounts", "sa",
}


def is_enabled():
    return os.environ.get(DEMO_ENV_VAR, "").strip().lower() in {"1", "true", "yes", "on"}


def _build_host_map(hostnames):
    """Mapa estável nome real -> pseudônimo. Ordenado para que a mesma máquina
    receba sempre o mesmo pseudônimo entre execuções e entre telas."""
    limpos = sorted({h for h in hostnames if isinstance(h, str) and h.strip()})
    return {h: f"servidor-{i:02d}" for i, h in enumerate(limpos, start=1)}


def _org_terms(machines, cloud_accounts):
    """Termos que identificam a organização: domínio Windows e as palavras próprias
    que aparecem nos nomes das integrações (ex.: 'Azure Acme Activity Logs' -> Acme)."""
    termos = set()
    if machines is not None and not machines.empty and "domain" in machines.columns:
        termos |= {d for d in machines["domain"].dropna().unique()
                   if isinstance(d, str) and d not in ("(none)", "")}
    for conta in (cloud_accounts or []):
        for palavra in re.findall(r"[A-Za-zÀ-ÿ]{3,}", conta.get("name") or ""):
            if palavra.lower() not in _STOPWORDS:
                termos.add(palavra)
    return {t for t in termos if len(t) >= 3}


def _scrub_text(text, host_map, org_terms):
    if not isinstance(text, str) or not text:
        return text
    for real, falso in host_map.items():
        text = re.sub(rf"\b{re.escape(real)}\b", falso, text, flags=re.IGNORECASE)
    # substring, sem \b: o nome da organização aparece grudado em outros tokens
    # (ex.: política customizada "LW_FIM_ACME"), e '_' conta como caractere de
    # palavra, então uma fronteira \b não casaria ali.
    for termo in org_terms:
        text = re.sub(re.escape(termo), "ORGANIZACAO", text, flags=re.IGNORECASE)
    # nomes de máquina/usuário citados em texto livre, mesmo fora do inventário atual
    text = HOSTS_LIST_RE.sub(lambda m: "Hosts: " + ", ".join(
        "servidor-xx" for _ in m.group(1).split(",")), text)
    text = HOST_PHRASE_RE.sub(lambda m: f"{m.group(1)} servidor-xx", text)
    text = USER_PHRASE_RE.sub("as user usuario", text)
    text = DASHED_NAME_RE.sub("servidor-xx", text)
    text = DOMAIN_USER_RE.sub("ORGANIZACAO\\\\usuario", text)
    text = EMAIL_RE.sub("usuario@exemplo.com", text)
    return text


def anonymize_data(data):
    """Recebe o dicionário de dados carregado e devolve uma cópia mascarada.
    Sem o modo demo ativo, devolve os dados originais sem tocar em nada."""
    if not is_enabled():
        return data

    data = dict(data)
    machines, vulns = data.get("machines"), data.get("vulns_critical_high")

    nomes = set()
    for df in (machines, vulns):
        if df is not None and not df.empty and "hostname" in df.columns:
            nomes |= set(df["hostname"].dropna())
    host_map = _build_host_map(nomes)

    dominios = _org_terms(machines, data.get("cloud_accounts"))

    if machines is not None and not machines.empty:
        machines = machines.copy()
        machines["hostname"] = machines["hostname"].map(lambda h: host_map.get(h, h))
        if "domain" in machines.columns:
            machines["domain"] = machines["domain"].map(
                lambda d: "ORGANIZACAO" if isinstance(d, str) and d in dominios else d)
        data["machines"] = machines

    if vulns is not None and not vulns.empty:
        vulns = vulns.copy()
        vulns["hostname"] = vulns["hostname"].map(lambda h: host_map.get(h, h))
        data["vulns_critical_high"] = vulns

    alerts = data.get("alerts")
    if alerts is not None and not alerts.empty:
        alerts = alerts.copy()
        # alertName também precisa passar: políticas customizadas podem levar o nome
        # da organização (ex.: "LW_FIM_ACME").
        for col in ("description", "alertName", "policyId"):
            if col in alerts.columns:
                alerts[col] = alerts[col].map(lambda t: _scrub_text(t, host_map, dominios))
        data["alerts"] = alerts

    contas = data.get("cloud_accounts")
    if contas:
        # Os identificadores de conta (tenantId / awsAccountId / projectId) NÃO podem
        # simplesmente sumir: são a chave que distingue "uma conta com duas
        # integrações" de "duas contas". Recebem um pseudônimo estável, preservando
        # a contagem correta sem revelar o identificador real.
        pseudo_ids, mascaradas = {}, []
        for i, conta in enumerate(contas, start=1):
            conta = dict(conta)
            tipo = (conta.get("type") or "")
            provedor = ("Azure" if tipo.startswith("Azure")
                        else "AWS" if tipo.upper().startswith("AWS")
                        else "GCP" if tipo.upper().startswith("GCP") else "Cloud")
            conta["name"] = f"Integração {provedor} {i}"
            conta["createdOrUpdatedBy"] = "usuario@exemplo.com"
            # o identificador da integração começa com o número da conta FortiCNAPP
            conta["intgGuid"] = f"DEMO-{provedor.upper()}-{i}"

            original = dict(conta.get("data") or {})
            mascarado = {}
            for campo in ("tenantId", "awsAccountId", "accountId", "projectId"):
                if original.get(campo):
                    real = original[campo]
                    pseudo_ids.setdefault(real, f"demo-conta-{len(pseudo_ids) + 1}")
                    mascarado[campo] = pseudo_ids[real]
            conta["data"] = mascarado  # credenciais descartadas, identificador pseudonimizado
            mascaradas.append(conta)
        data["cloud_accounts"] = mascaradas

    return data
