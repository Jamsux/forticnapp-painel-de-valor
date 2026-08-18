#!/usr/bin/env python3
"""Puxa dados atuais do FortiCNAPP do cliente e cacheia localmente em data/.
Rodar antes de abrir os dashboards (ou periodicamente): python3 scripts/refresh_data.py
"""
import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.forticnapp_client import ForticnappClient
from src.collectors import alerts, vulnerabilities, entities, inventory
from src import cache
from src.config_store import CredentialsNotConfigured


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alert-days", type=int, default=90, help="janela de histórico de alertas (dias)")
    parser.add_argument("--vuln-lookback-days", type=int, default=1, help="janela do snapshot de vulnerabilidades ativas (dias)")
    args = parser.parse_args()

    try:
        client = ForticnappClient()
    except CredentialsNotConfigured as exc:
        print(f"[erro] {exc}")
        sys.exit(1)
    now = dt.datetime.now(dt.timezone.utc)

    print(f"[{now.isoformat()}] Autenticando e iniciando coleta...")

    print(f"-> Alertas (últimos {args.alert_days} dias)...")
    alerts_df = alerts.fetch_alerts(client, days=args.alert_days, now=now)
    cache.save_df("alerts", alerts_df)
    print(f"   {len(alerts_df)} alertas coletados.")

    print("-> Vulnerabilidades ativas (contagem por severidade)...")
    vuln_counts = vulnerabilities.fetch_severity_counts(client, now=now, lookback_days=args.vuln_lookback_days)
    cache.save_json("vuln_severity_counts", vuln_counts)
    print(f"   {vuln_counts}")

    print("-> Vulnerabilidades Critical/High (detalhe)...")
    vuln_df = vulnerabilities.fetch_critical_high_detail(client, now=now, lookback_days=args.vuln_lookback_days)
    cache.save_df("vulns_critical_high", vuln_df)
    print(f"   {len(vuln_df)} avaliações críticas/altas (deduplicadas por host+CVE).")

    print("-> Inventário de hosts (MachineDetails)...")
    machines_df = entities.fetch_machine_details(client)
    cache.save_df("machines", machines_df)
    print(f"   {len(machines_df)} hosts monitorados.")

    print("-> Contagens de visibilidade (containers, usuários, apps, pacotes...)...")
    visibility_counts = entities.fetch_visibility_counts(client)
    cache.save_json("visibility_counts", visibility_counts)
    print(f"   {visibility_counts}")

    print("-> Contexto de conta (cloud accounts, contrato, regras)...")
    for name, fetch_fn in [
        ("cloud_accounts", inventory.fetch_cloud_accounts),
        ("contract_info", inventory.fetch_contract_info),
        ("alert_rules", inventory.fetch_alert_rules),
        ("report_rules", inventory.fetch_report_rules),
        ("resource_groups", inventory.fetch_resource_groups),
    ]:
        try:
            cache.save_json(name, fetch_fn(client))
        except Exception as exc:
            print(f"   [aviso] falha ao coletar {name}: {exc}")

    cache.save_json("_refresh_meta", {"refreshed_at": now.isoformat(), "alert_days": args.alert_days})
    print("Coleta concluída. Dados salvos em data/.")


if __name__ == "__main__":
    main()
