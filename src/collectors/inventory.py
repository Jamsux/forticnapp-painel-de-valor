"""Coleta de contexto de conta: contas cloud monitoradas, contrato, regras de alerta."""


def fetch_cloud_accounts(client):
    resp = client.get("/api/v2/CloudAccounts")
    return resp.get("data", [])


def fetch_contract_info(client):
    resp = client.get("/api/v2/ContractInfo")
    return resp.get("data", [])


def fetch_alert_rules(client):
    resp = client.get("/api/v2/AlertRules")
    return resp.get("data", [])


def fetch_report_rules(client):
    resp = client.get("/api/v2/ReportRules")
    return resp.get("data", [])


def fetch_resource_groups(client):
    resp = client.get("/api/v2/ResourceGroups")
    return resp.get("data", [])
