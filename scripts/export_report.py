#!/usr/bin/env python3
"""Gera o relatório como HTML autocontido (e opcionalmente PDF) sem abrir o dashboard.

    python3 scripts/export_report.py --out relatorio.html
    python3 scripts/export_report.py --out relatorio.pdf --pdf

O PDF usa o Chrome/Chromium instalado em modo headless — mesmo motor de impressão
que o botão "Imprimir / Salvar como PDF" do dashboard, então o resultado é fiel.
"""
import argparse
import datetime as dt
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import anonymize, browser, cache, report  # noqa: E402
from src.aggregate import RETENTION_DAYS  # noqa: E402


def load_data():
    return anonymize.anonymize_data({
        "alerts": cache.load_df("alerts"),
        "vuln_severity_counts": cache.load_json("vuln_severity_counts"),
        "vulns_critical_high": cache.load_df("vulns_critical_high"),
        "machines": cache.load_df("machines"),
        "visibility_counts": cache.load_json("visibility_counts"),
        "cloud_accounts": cache.load_json("cloud_accounts"),
        "contract_info": cache.load_json("contract_info"),
    })


def resolve_period(args):
    """Traduz --days / --from / --to em (início, fim). Sem nenhum deles, usa tudo
    o que foi coletado."""
    import pandas as pd

    now = pd.Timestamp(dt.datetime.now(dt.timezone.utc))
    end = pd.Timestamp(args.date_to, tz="UTC") + pd.Timedelta(days=1) if args.date_to else now
    if args.date_from:
        return pd.Timestamp(args.date_from, tz="UTC"), end
    if args.days:
        if args.days > RETENTION_DAYS:
            print(f"[aviso] a API do FortiCNAPP retém {RETENTION_DAYS} dias; "
                  f"usando {RETENTION_DAYS} em vez de {args.days}.")
        return end - pd.Timedelta(days=min(args.days, RETENTION_DAYS)), end
    return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="relatorio.html", help="arquivo de saída")
    parser.add_argument("--client-name", default="", help="nome que aparece no cabeçalho")
    parser.add_argument("--no-ops", action="store_true", help="omite o anexo operacional")
    parser.add_argument("--no-glossary", action="store_true", help="omite o glossário")
    parser.add_argument("--pdf", action="store_true", help="gera PDF via Chrome headless")
    parser.add_argument("--days", type=int, default=None,
                        help="período dos indicadores de alertas, em dias (ex.: 30). "
                             "Máximo 90 — é o que a API do FortiCNAPP retém.")
    parser.add_argument("--from", dest="date_from", default=None,
                        help="data inicial no formato AAAA-MM-DD (alternativa a --days)")
    parser.add_argument("--to", dest="date_to", default=None,
                        help="data final no formato AAAA-MM-DD (padrão: hoje)")
    args = parser.parse_args()

    if cache.load_json("_refresh_meta") is None:
        print("[erro] Nenhum dado coletado ainda. Rode antes: python3 scripts/refresh_data.py")
        sys.exit(1)

    period_start, period_end = resolve_period(args)
    html = report.standalone_html(report.build_report_html(
        load_data(),
        client_name=args.client_name,
        include_ops=not args.no_ops,
        include_glossary=not args.no_glossary,
        period_start=period_start,
        period_end=period_end,
    ))

    if not args.pdf:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"HTML gerado: {args.out}")
        return

    chrome = browser.find_chrome()
    if not chrome:
        print(f"[erro] {browser.MENSAGEM_AUSENTE}")
        sys.exit(1)

    tmp_html = os.path.abspath(args.out + ".tmp.html")
    with open(tmp_html, "w", encoding="utf-8") as fh:
        fh.write(html)
    try:
        subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
             f"--print-to-pdf={os.path.abspath(args.out)}", pathlib.Path(tmp_html).as_uri()],
            check=True, capture_output=True, timeout=120,
        )
        print(f"PDF gerado: {args.out}")
    finally:
        os.remove(tmp_html)


if __name__ == "__main__":
    main()
