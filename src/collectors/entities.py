"""Coleta de entidades: inventário de hosts monitorados + contagens de visibilidade.

Importante: as APIs Entities/* devolvem um registro por OBSERVAÇÃO/check-in do
agente (várias vezes ao dia), não um registro por entidade única. Usar
paging.totalRows direto superestima tudo — em alguns casos (Users, Applications)
por 30-40x. Por isso cada contagem aqui deduplica por uma chave natural
(mid + nome/identificador) em vez de contar linhas brutas.
"""
import pandas as pd


def fetch_machine_details(client):
    resp = client.post("/api/v2/Entities/MachineDetails/search", {})
    rows = resp.get("data", [])
    if not rows:
        return pd.DataFrame(columns=["mid", "hostname", "os", "domain", "createdTime"])
    df = pd.DataFrame([
        {
            "mid": r.get("mid"),
            "hostname": r.get("hostname"),
            "os": r.get("os"),
            "domain": r.get("domain"),
            "createdTime": r.get("createdTime"),
        }
        for r in rows
    ])
    df["createdTime"] = pd.to_datetime(df["createdTime"], errors="coerce", utc=True)
    # Mesmo mid aparece repetido (um por check-in do agente) — fica só a observação
    # mais recente de cada host.
    df = df.sort_values("createdTime").drop_duplicates(subset="mid", keep="last").reset_index(drop=True)
    return df


def fetch_visibility_counts(client):
    """Contagens de entidades ÚNICAS (host+usuário, host+app, ...), não linhas brutas."""
    counts = {}

    machines = client.post("/api/v2/Entities/MachineDetails/search", {}).get("data", [])
    counts["hosts"] = len({m.get("mid") for m in machines})

    containers = client.post("/api/v2/Entities/Containers/search", {}).get("data", [])
    counts["containers"] = len({c.get("mid") for c in containers})

    users = client.search_all_pages(
        "/api/v2/Entities/Users/search", {"returns": ["mid", "username"]}, max_pages=20
    )
    counts["users_os"] = len({(u.get("mid"), u.get("username")) for u in users})

    apps = client.search_all_pages(
        "/api/v2/Entities/Applications/search", {"returns": ["mid", "appName"]}, max_pages=20
    )
    counts["applications"] = len({(a.get("mid"), a.get("appName")) for a in apps})

    network_interfaces = client.post("/api/v2/Entities/NetworkInterfaces/search", {}).get("data", [])
    counts["network_interfaces"] = len({(n.get("mid"), n.get("hwAddr"), n.get("name")) for n in network_interfaces})

    # Packages: só a 1a página (~5.000 linhas) já mostrou ~96% de linhas únicas por
    # (mid, packageName, version) — ao contrário das outras entidades, aqui a API
    # parece não reemitir a mesma linha a cada check-in. Paginar as ~90 páginas
    # completas (~400k linhas) custaria ~1-2 min extra de refresh por uma correção
    # de poucos % — não compensa. Usamos o total bruto da API como aproximação.
    packages_resp = client.post("/api/v2/Entities/Packages/search", {"returns": ["mid"]})
    counts["packages"] = packages_resp.get("paging", {}).get("totalRows", len(packages_resp.get("data", [])))

    return counts
