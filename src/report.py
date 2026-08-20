"""Gera o HTML do relatório profissional para impressão/PDF (via impressão do navegador)."""
import datetime as dt
import html as _html

from . import aggregate
from .aggregate import RETENTION_DAYS
from .glossary import (alert_type_label, entries as glossary_entries, help_text,
                       label as glossary_label)
from .i18n import get_language, t
from .theme import PALETTE, SEVERITY_COLOR_MAP, category_label, severity_label

REPORT_CSS = f"""
<style>
@media print {{
  @page {{ size: A4; margin: 14mm 12mm; }}

  [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"],
  [data-testid="stStatusWidget"], [data-testid="stDecoration"], [data-testid="stBottomBlockContainer"],
  .st-key-report_controls, header, footer, #MainMenu {{
    display: none !important;
  }}

  /* O Streamlit renderiza o conteúdo dentro de contêineres com altura fixa e
     overflow:auto (scroll). Na impressão isso recorta tudo que passa da primeira
     página — precisa virar fluxo normal para o conteúdo paginar. */
  html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
  [data-testid="stMainBlockContainer"], .main, .main .block-container,
  section[tabindex="0"], .stMainBlockContainer {{
    overflow: visible !important;
    height: auto !important;
    max-height: none !important;
    min-height: 0 !important;
    position: static !important;
    display: block !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
    width: auto !important;
    transform: none !important;
  }}

  .stApp {{ background: white !important; }}
  .print-report {{ box-shadow: none !important; border: none !important; margin: 0 !important; padding: 0 !important; }}

  /* Sem isso o navegador remove as cores de fundo — as barras de severidade e a
     faixa do cabeçalho sairiam em branco no papel. */
  * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}

  /* NÃO usar break-inside:avoid em .rp-section: seções longas (glossário, anexo)
     não cabem numa página e o navegador acaba recortando o excedente em vez de
     paginar. A quebra é evitada nos BLOCOS, que sempre cabem em uma página. */
  .rp-section {{ break-inside: auto; page-break-inside: auto; }}

  /* .rp-block = título + seu conteúdo (tabela/gráfico). Mantém os dois juntos:
     nunca um cabeçalho no fim de uma página e a tabela na página seguinte, nem
     tabela partida ao meio. Se não couber no espaço restante, o bloco inteiro
     desce para a próxima página. */
  .rp-block, table.rp-table, .rp-kpi, .rp-gloss-item, .rp-bar-row, .rp-bars,
  .rp-callout, .rp-kpi-grid {{
    break-inside: avoid; page-break-inside: avoid;
  }}
  .rp-section > h2, .rp-section h3 {{ break-after: avoid; page-break-after: avoid; }}
  .rp-header {{ break-after: avoid; page-break-after: avoid; }}

  /* Multi-coluna quebra de forma imprevisível entre páginas (foi o que recortava
     o glossário no meio da linha) — no papel vira coluna única. */
  .rp-gloss {{ column-count: 1 !important; }}

  /* Na tela o flex-wrap se ajusta bem, mas na largura da página ele calcula
     quantos cards cabem pelo flex-basis e depois os cresce, estourando a margem
     direita (o último card saía cortado). Grid de 3 colunas 1fr é determinístico:
     cada coluna é exatamente (largura - gaps) / 3, então não há como transbordar. */
  .rp-kpi-grid {{
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
  }}
  .rp-kpi {{ width: auto !important; flex: none !important; }}

  /* Se ainda assim uma tabela for maior que uma página, o cabeçalho se repete e
     nenhuma linha é partida — rede de segurança para o caso extremo. */
  table.rp-table thead {{ display: table-header-group; }}
  table.rp-table tr {{ break-inside: avoid; page-break-inside: avoid; }}
  p, li {{ orphans: 3; widows: 3; }}
}}
@media screen {{
  .print-report {{
    max-width: 880px; margin: 0 auto 40px auto; background: white;
    padding: 40px 48px; border: 1px solid {PALETTE["border"]}; border-radius: 10px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
  }}
}}
.print-report {{
  font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  color: {PALETTE["ink"]};
  line-height: 1.45;
  max-width: 100%;
}}
/* Sem border-box, o padding e a borda dos cards somam por FORA da largura que o
   flex distribuiu — a linha de cards fica mais larga que a página e o último card
   sai cortado na margem direita ao imprimir. */
.print-report, .print-report * {{ box-sizing: border-box; }}
.print-report h1, .print-report h2, .print-report h3 {{
  font-family: inherit; color: {PALETTE["ink"]}; margin: 0;
}}
.rp-header {{
  display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 3px solid {PALETTE["accent"]}; padding-bottom: 14px; margin-bottom: 24px;
}}
.rp-header .rp-brand {{ font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase;
  color: {PALETTE["muted"]}; font-weight: 600; margin-bottom: 4px; }}
.rp-header h1 {{ font-size: 26px; font-weight: 750; }}
.rp-header .rp-meta {{ text-align: right; font-size: 12.5px; color: {PALETTE["muted"]}; }}
.rp-section {{ margin: 22px 0; }}
.rp-block {{ margin-bottom: 16px; }}
.rp-block:last-child {{ margin-bottom: 0; }}
/* Título de bloco (nível abaixo da seção) */
.rp-block-title {{
  font-size: 12px; font-weight: 700; color: {PALETTE["ink"]};
  margin: 0 0 7px 0;
}}
.rp-note {{ font-size: 11px; color: {PALETTE["muted"]}; line-height: 1.45; margin: 8px 0 0 0; }}
/* Severidade com a cor da própria gravidade, para leitura imediata na impressão */
.rp-sev {{ font-weight: 700; }}
.rp-sev-dot {{
  display: inline-block; width: 7px; height: 7px; border-radius: 50%;
  margin-right: 5px; vertical-align: middle;
}}
.rp-section h2 {{
  font-size: 15px; text-transform: uppercase; letter-spacing: 0.05em;
  color: {PALETTE["accent"]}; border-bottom: 1px solid {PALETTE["border"]};
  padding-bottom: 6px; margin-bottom: 14px;
}}
.rp-callout {{
  background: #F1F5F9; border-left: 4px solid {PALETTE["accent"]}; border-radius: 4px;
  padding: 14px 18px; font-size: 14.5px; margin-bottom: 18px;
}}
.rp-kpi-grid {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 8px; max-width: 100%; }}
.rp-kpi {{
  min-width: 0;  /* permite o card encolher; sem isso o texto longo do rótulo alarga a linha */
  flex: 1 1 150px; border: 1px solid {PALETTE["border"]}; border-radius: 8px;
  padding: 10px 12px; break-inside: avoid;
}}
.rp-kpi .rp-kpi-label {{ font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.04em;
  color: {PALETTE["muted"]}; font-weight: 600; margin-bottom: 4px; overflow-wrap: break-word; }}
.rp-kpi .rp-kpi-value {{ font-size: 24px; font-weight: 750; color: {PALETTE["ink"]}; }}
.rp-kpi .rp-kpi-sub {{ font-size: 11px; color: {PALETTE["muted"]}; margin-top: 2px; }}
.rp-kpi-hint {{
  display: inline-flex; align-items: center; justify-content: center;
  width: 12px; height: 12px; margin-left: 4px; border-radius: 50%;
  border: 1px solid {PALETTE["muted"]}; color: {PALETTE["muted"]};
  font-size: 8.5px; font-weight: 700; cursor: help; vertical-align: middle;
}}
@media print {{ .rp-kpi-hint {{ display: none !important; }} }}
.rp-gloss {{ column-count: 2; column-gap: 26px; }}
.rp-gloss-item {{ break-inside: avoid; margin-bottom: 9px; font-size: 11px; line-height: 1.4; }}
.rp-gloss-term {{ display: block; font-weight: 700; color: {PALETTE["ink"]}; }}
.rp-gloss-def {{ color: {PALETTE["muted"]}; }}
table.rp-table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; margin-bottom: 6px; }}
table.rp-table th {{
  text-align: left; font-size: 10.5px; text-transform: uppercase; color: {PALETTE["muted"]};
  border-bottom: 1px solid {PALETTE["ink"]}; padding: 6px 8px; letter-spacing: 0.03em;
}}
table.rp-table td {{ padding: 6px 8px; border-bottom: 1px solid {PALETTE["border"]}; }}
table.rp-table tr:last-child td {{ border-bottom: none; }}
.rp-bars {{ margin-bottom: 8px; max-width: 100%; }}
.rp-bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 7px; font-size: 12.5px; }}
.rp-bar-label {{ width: 110px; flex-shrink: 0; color: {PALETTE["ink"]}; }}
.rp-bar-track {{ flex: 1; background: #F1F5F9; border-radius: 3px; height: 14px; overflow: hidden; }}
.rp-bar-fill {{ height: 100%; border-radius: 3px; }}
.rp-bar-value {{ width: 55px; text-align: right; flex-shrink: 0; color: {PALETTE["muted"]}; font-variant-numeric: tabular-nums; }}
.rp-badge {{
  display: inline-block; padding: 1px 8px; border-radius: 10px; font-size: 11px; font-weight: 600;
  color: white;
}}
.rp-footer {{
  margin-top: 32px; padding-top: 12px; border-top: 1px solid {PALETTE["border"]};
  font-size: 10.5px; color: {PALETTE["muted"]};
}}
</style>
"""


def esc(value):
    return _html.escape("" if value is None else str(value))


def kpi_card(label, value, sub="", tooltip=""):
    # HTML gerado numa única linha por elemento: o parser de markdown do Streamlit
    # interpreta uma linha em branco no meio de um bloco de HTML bruto como o fim
    # do bloco, e passa a escapar tudo que vem depois como texto.
    sub_html = f'<div class="rp-kpi-sub">{esc(sub)}</div>' if sub else ""
    # title= dá o tooltip nativo do navegador na tela; no papel ele desaparece, por
    # isso as mesmas definições também são impressas no glossário ao final.
    title_attr = f' title="{esc(tooltip)}"' if tooltip else ""
    hint = '<span class="rp-kpi-hint">?</span>' if tooltip else ""
    return (
        f'<div class="rp-kpi"{title_attr}>'
        f'<div class="rp-kpi-label">{esc(label)}{hint}</div>'
        f'<div class="rp-kpi-value">{esc(value)}</div>'
        f"{sub_html}</div>"
    )


def glossary_section(entries):
    """Glossário impresso: lista de (rótulo, definição). Tooltips somem no papel,
    então as mesmas definições viram uma seção de referência no fim do relatório."""
    if not entries:
        return ""
    items = "".join(
        f'<div class="rp-gloss-item"><span class="rp-gloss-term">{esc(term)}</span>'
        f'<span class="rp-gloss-def">{esc(definition)}</span></div>'
        for term, definition in entries
    )
    return f'<div class="rp-gloss">{items}</div>'


def kpi_grid(cards):
    return f'<div class="rp-kpi-grid">{"".join(cards)}</div>'


def bar_list(rows, max_value=None, colors=None):
    """rows: lista de (label, valor). colors: dict label->cor hex opcional.
    Quando há cor para o rótulo, o texto também recebe essa cor — na impressão a
    gravidade precisa ser legível sem depender só do comprimento da barra."""
    if not rows:
        return f'<p style="color:#94A3B8;font-size:12.5px;">{esc(t("doc.no_data"))}</p>'
    max_value = max_value or max((v for _, v in rows), default=1) or 1
    out = []
    for label, value in rows:
        pct = min(100, round(100 * value / max_value)) if max_value else 0
        color = (colors or {}).get(label)
        bar_color = color or PALETTE["accent"]
        label_style = f' style="color:{color};font-weight:700;"' if color else ""
        value_str = esc(num(value))
        out.append(
            '<div class="rp-bar-row">'
            f'<div class="rp-bar-label"{label_style}>{esc(label)}</div>'
            f'<div class="rp-bar-track"><div class="rp-bar-fill" style="width:{pct}%;background:{bar_color};"></div></div>'
            f'<div class="rp-bar-value">{value_str}</div>'
            "</div>"
        )
    # agrupado para o conjunto de barras não ser partido ao meio numa quebra de página
    return f'<div class="rp-bars">{"".join(out)}</div>'


def table(headers, rows, html_cols=(), align_right=()):
    """rows: lista de listas/tuplas já formatadas.
    html_cols: índices de colunas cujo conteúdo já é HTML (não deve ser escapado).
    align_right: índices de colunas numéricas, alinhadas à direita."""
    if not rows:
        return f'<p style="color:#94A3B8;font-size:12.5px;">{esc(t("doc.no_data"))}</p>'
    thead = "".join(
        f'<th{" style=\"text-align:right;\"" if i in align_right else ""}>{esc(h)}</th>'
        for i, h in enumerate(headers)
    )
    trs = []
    for row in rows:
        tds = "".join(
            f'<td{" style=\"text-align:right;font-variant-numeric:tabular-nums;\"" if i in align_right else ""}>'
            f'{v if i in html_cols else esc(v)}</td>'
            for i, v in enumerate(row)
        )
        trs.append(f"<tr>{tds}</tr>")
    return f'<table class="rp-table"><thead><tr>{thead}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def severity_text(severity):
    """Severidade escrita na cor da própria gravidade (com marcador), para que
    Critical/High saltem aos olhos também no papel. A cor vem do valor original
    da API; o texto exibido é o rótulo no idioma corrente."""
    color = SEVERITY_COLOR_MAP.get(severity, PALETTE["muted"])
    return (
        f'<span class="rp-sev" style="color:{color};">'
        f'<span class="rp-sev-dot" style="background:{color};"></span>'
        f"{esc(severity_label(severity))}</span>"
    )


def severity_badge(severity):
    color = SEVERITY_COLOR_MAP.get(severity, PALETTE["muted"])
    return f'<span class="rp-badge" style="background:{color};">{esc(severity)}</span>'


def block(title, body_html):
    """Título + conteúdo que nunca se separam numa quebra de página."""
    title_html = f'<div class="rp-block-title">{esc(title)}</div>' if title else ""
    return f'<div class="rp-block">{title_html}{body_html}</div>'


def section(title, body_html):
    return f'<div class="rp-section"><h2>{esc(title)}</h2>{body_html}</div>'


def header(client_name, generated_at_str, period_label):
    subtitle = esc(client_name) if client_name else t("doc.default_title")
    return (
        '<div class="rp-header"><div>'
        f'<div class="rp-brand">{esc(t("doc.brand"))}</div>'
        f"<h1>{subtitle}</h1></div>"
        f'<div class="rp-meta">{esc(t("doc.generated_at", when=generated_at_str))}<br/>'
        f'{esc(t("doc.period", period=period_label))}</div></div>'
    )


def footer(generated_at_str):
    return (
        '<div class="rp-footer">'
        f'{esc(t("doc.footer", when=generated_at_str))}'
        "</div>"
    )


VC_HELP_KEYS = {
    "hosts": "coverage_hosts", "containers": "coverage_containers", "users_os": "coverage_users",
    "applications": "coverage_applications", "network_interfaces": "coverage_network_interfaces",
    "packages": "coverage_packages",
}


def num(valor):
    """Separador de milhar conforme o idioma: 1,234 em inglês, 1.234 em português."""
    formatado = f"{valor:,}"
    return formatado if get_language() == "en" else formatado.replace(",", ".")


def _fmt_date(momento):
    return momento.strftime("%b %d, %Y" if get_language() == "en" else "%d/%m/%Y")


def build_report_html(data, client_name="", include_ops=True, include_glossary=True, now=None,
                      period_start=None, period_end=None):
    """Monta o relatório completo a partir dos dados cacheados.

    period_start/period_end recortam os indicadores de ALERTAS. Vulnerabilidades e
    inventário são a fotografia do momento da coleta — não têm recorte temporal, e
    isso fica dito no próprio relatório para não induzir leitura errada.

    Vive aqui (e não na página Streamlit) para que a geração possa ser exercitada
    fora do app — testes de paginação/impressão usam exatamente este mesmo HTML.
    """
    alerts_df = aggregate.filter_by_period(data["alerts"], period_start, period_end)
    vuln_df = data["vulns_critical_high"]
    vuln_counts = data["vuln_severity_counts"]

    akpi = aggregate.alert_headline_kpis(alerts_df)
    rkpi = aggregate.resolution_time_kpis(alerts_df)
    vkpi = aggregate.vuln_kpis(vuln_counts, vuln_df)
    cov = aggregate.coverage_summary(data["machines"], data["visibility_counts"], data["cloud_accounts"])

    now = now or dt.datetime.now(dt.timezone.utc)
    generated_at_str = now.strftime("%d/%m/%Y %H:%M UTC")
    # o período efetivo é o solicitado; sem solicitação, o que existe nos dados
    ini = period_start if period_start is not None else (
        alerts_df["startTime"].min() if alerts_df is not None and not alerts_df.empty else None)
    fim = period_end if period_end is not None else now
    period_label = f"{_fmt_date(ini)} – {_fmt_date(fim)}" if ini is not None else "—"

    parts = [header(client_name, generated_at_str, period_label)]

    # --- Resumo executivo
    headline = ""
    if akpi["total"]:
        headline = t("doc.headline", total=num(akpi["total"]), open_pct=akpi["open_pct"],
                     open=num(akpi["open"]), age=akpi["avg_open_age_days"])
    cards = [
        kpi_card(t("doc.kpi.alerts_period"), num(akpi["total"]), tooltip=help_text("alerts_total")),
        kpi_card(glossary_label("alerts_open_pct"), f"{akpi['open_pct']}%",
                 tooltip=help_text("alerts_open_pct")),
        kpi_card(glossary_label("alerts_critical_high_open"), akpi["critical_high_open"],
                 tooltip=help_text("alerts_critical_high_open")),
        kpi_card(glossary_label("alerts_avg_age"),
                 f"{akpi['avg_open_age_days']} {t('unit.days')}",
                 tooltip=help_text("alerts_avg_age")),
        kpi_card(glossary_label("vulns_critical_high"), num(vkpi["critical_high_active"]),
                 tooltip=help_text("vulns_critical_high")),
        kpi_card(glossary_label("coverage_hosts"), cov["hosts_total"],
                 tooltip=help_text("coverage_hosts")),
    ]
    body = (f'<div class="rp-callout">{headline}</div>' if headline else "") + kpi_grid(cards)
    parts.append(section(t("doc.section.executive"), body))

    # --- Tempo de resposta
    sem_amostra = rkpi["sample_size"] == 0
    r_cards = [
        kpi_card(glossary_label("mttr_median"),
                 "—" if sem_amostra else f"{rkpi['mttr_days_median']} {t('unit.days')}",
                 t("doc.kpi.sample_of", n=num(rkpi["sample_size"])), tooltip=help_text("mttr_median")),
        kpi_card(glossary_label("mttr_p90"),
                 "—" if sem_amostra else f"{rkpi['mttr_days_p90']} {t('unit.days')}",
                 tooltip=help_text("mttr_p90")),
        kpi_card(t("doc.kpi.open_no_touch"), f"{rkpi['open_never_touched_pct']}%",
                 t("doc.kpi.of_total", part=num(rkpi["open_never_touched"]),
                   total=num(rkpi["open_total"])),
                 tooltip=help_text("open_never_touched")),
    ]
    mttr_sev = aggregate.mttr_by_severity(alerts_df)
    mttr_table = table(
        [t("doc.col.severity"), t("doc.col.mttr_days")],
        [[severity_text(row.severity), row.mttr_days] for row in mttr_sev.itertuples()],
        html_cols={0}, align_right={1},
    )
    note = f'<p class="rp-note">{t("doc.note.how_to_read")}</p>'
    period_days = (fim - ini).days if ini is not None and fim is not None else RETENTION_DAYS
    bias = aggregate.response_bias_note(period_days, rkpi["sample_size"])
    if bias:
        note += (f'<p class="rp-note" style="border-left:3px solid {PALETTE["medium"]};'
                 f'padding-left:9px;">{t("doc.note.period_warning")}{esc(bias)}</p>')
    parts.append(section(
        t("doc.section.response"),
        block("", kpi_grid(r_cards)) + block(t("doc.block.mttr_by_sev"), mttr_table + note),
    ))

    # --- Vulnerabilidades
    sev_rows = [(severity_label(s), vkpi["counts"].get(s, 0))
                for s in aggregate.SEVERITY_ORDER if vkpi["counts"].get(s, 0)]
    sev_colors = {severity_label(s): c for s, c in SEVERITY_COLOR_MAP.items()}
    v_cards = [
        kpi_card(glossary_label("vulns_known_exploited"), num(vkpi["known_exploited"]),
                 t("doc.kpi.attack_tool"), tooltip=help_text("vulns_known_exploited")),
        kpi_card(glossary_label("vulns_malware"), num(vkpi["malware_associated"]),
                 tooltip=help_text("vulns_malware")),
        kpi_card(glossary_label("vulns_fixable"), num(vkpi["fixable_now"]),
                 tooltip=help_text("vulns_fixable")),
        kpi_card(glossary_label("vulns_hosts_affected"), num(vkpi["hosts_affected"]),
                 tooltip=help_text("vulns_hosts_affected")),
        kpi_card(glossary_label("vulns_wormable"), num(vkpi["wormable"]),
                 tooltip=help_text("vulns_wormable")),
        kpi_card(t("doc.kpi.total_active"), num(vkpi["total_active"]), t("doc.kpi.all_severities")),
    ]
    known = aggregate.known_exploited_table(vuln_df, n=10)
    known_rows = [
        [r.hostname, r.vulnId, severity_text(r.severity), r.cveRiskScore,
         t("doc.yes") if r.fixAvailable else t("doc.no")]
        for r in known.itertuples()
    ] if not known.empty else []
    known_block = block(
        t("doc.block.top_exploited"),
        table([t("doc.col.server"), t("doc.col.cve"), t("doc.col.severity"), t("doc.col.cvss"),
               t("doc.col.fix_available")],
              known_rows, html_cols={2}, align_right={3})
        + f'<p class="rp-note">{t("doc.note.cvss")}</p>',
    ) if known_rows else ""
    snapshot_note = f'<p class="rp-note">{t("doc.note.snapshot_vulns", when=generated_at_str)}</p>'
    parts.append(section(
        t("doc.section.vulns"),
        block(t("doc.block.severity_dist"),
              bar_list(sev_rows, colors=sev_colors) + snapshot_note)
        + block("", kpi_grid(v_cards))
        + known_block,
    ))

    # --- Tipos de alerta mais frequentes (o que o produto vem detectando)
    top_types = aggregate.top_alert_types(alerts_df, n=8)
    if not top_types.empty:
        total_alerts = akpi["total"] or 1
        type_rows = [
            [alert_type_label(r.alertType), num(r.count),
             f"{round(100 * r.count / total_alerts, 1)}%"]
            for r in top_types.itertuples()
        ]
        concentracao = round(100 * top_types["count"].head(3).sum() / total_alerts, 1)
        parts.append(section(
            t("doc.section.detecting"),
            block(
                t("doc.block.alert_types"),
                table([t("doc.col.detected"), t("doc.col.occurrences"), t("doc.col.pct_total")],
                      type_rows, align_right={1, 2})
                + f'<p class="rp-note">{t("doc.note.alert_types", pct=concentracao)}</p>',
            ),
        ))

    # --- Cobertura
    vc = cov["visibility_counts"] or {}
    cov_cards = [
        kpi_card(glossary_label(VC_HELP_KEYS[k]) if k in VC_HELP_KEYS else k, num(v),
                 tooltip=help_text(VC_HELP_KEYS[k]) if k in VC_HELP_KEYS else "")
        for k, v in vc.items()
    ]
    cov_cards.append(kpi_card(
        glossary_label("coverage_cloud_accounts"), cov["cloud_accounts_total"],
        t("doc.kpi.integrations", n=cov["cloud_integrations_total"]),
        tooltip=help_text("coverage_cloud_accounts"),
    ))
    parts.append(section(
        t("doc.section.coverage"),
        block("", kpi_grid(cov_cards)
              + f'<p class="rp-note">{t("doc.note.snapshot_coverage")}</p>'),
    ))

    # --- Anexo operacional
    if include_ops:
        LIMITE_ALERTAS = 20
        open_df = aggregate.open_alerts_table(alerts_df)
        alerts_title = t("doc.block.open_alerts")
        if not open_df.empty:
            crit_high_all = open_df[open_df["severity"].isin(["Critical", "High"])]
            crit_high = crit_high_all.head(LIMITE_ALERTAS)
            # o título só promete "top N" quando de fato houve corte
            if len(crit_high_all) > LIMITE_ALERTAS:
                alerts_title += t("doc.block.open_alerts_capped", n=LIMITE_ALERTAS,
                                  total=len(crit_high_all))
            else:
                alerts_title += t("doc.block.open_alerts_all", n=len(crit_high_all))
            rows = [[r.alertName, severity_text(r.severity), category_label(r.category),
                     round(r.age_days, 1)]
                    for r in crit_high.itertuples()]
            alerts_table_html = table(
                [t("doc.col.alert"), t("doc.col.severity"), t("doc.col.source"),
                 t("doc.col.idle_days")],
                rows, html_cols={1}, align_right={3})
        else:
            alerts_table_html = f"<p>{esc(t('ops.open_alerts_empty'))}</p>"

        top_hosts = aggregate.top_vulnerable_hosts(vuln_df, n=10)
        hosts_rows = ([[r.hostname, r.critical, r.high, r.total] for r in top_hosts.itertuples()]
                      if not top_hosts.empty else [])
        ops_html = (
            block(alerts_title, alerts_table_html)
            + block(t("doc.block.top_hosts"),
                    table([t("doc.col.server"), t("doc.col.critical"), t("doc.col.high"),
                           t("doc.col.total")], hosts_rows, align_right={1, 2, 3}))
        )
        parts.append(section(t("doc.section.annex"), ops_html))

    # --- Glossário (tooltips não existem no papel)
    if include_glossary:
        glossary_keys = [
            "alerts_total", "alerts_open_pct", "alerts_critical_high_open", "alerts_avg_age",
            "mttr_median", "mttr_p90", "open_never_touched", "mttr_by_severity",
            "vulns_critical_high", "vulns_by_severity", "vulns_known_exploited", "vulns_malware",
            "vulns_wormable", "vulns_fixable", "vulns_hosts_affected",
            "top_alert_types",
        ]
        glossary_keys += [VC_HELP_KEYS[k] for k in vc if k in VC_HELP_KEYS]
        glossary_keys.append("coverage_cloud_accounts")
        if include_ops:
            glossary_keys += ["open_alerts_table", "top_vulnerable_hosts"]
        parts.append(section(t("doc.section.glossary"),
                             glossary_section(glossary_entries(glossary_keys))))

    parts.append(footer(generated_at_str))
    return f'<div class="print-report">{"".join(parts)}</div>'


def standalone_html(report_html):
    """Documento HTML completo e autocontido — usado para gerar/validar o PDF fora do Streamlit."""
    lang = get_language()
    return (
        f'<!doctype html><html lang="{"en" if lang == "en" else "pt-BR"}"><head><meta charset="utf-8">'
        f"<title>{esc(t('doc.default_title'))}</title>"
        f"{REPORT_CSS}</head><body>{report_html}</body></html>"
    )
