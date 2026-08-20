"""Textos da interface em inglês e português.

O idioma corrente é guardado por thread: cada sessão do Streamlit roda na sua
própria thread, então dois navegadores abertos ao mesmo tempo podem usar idiomas
diferentes sem interferir um no outro. Scripts de linha de comando usam a
variável de ambiente APP_LANG ou o parâmetro --lang.

Inglês é o padrão; português é a alternativa.
"""
import os
import threading

DEFAULT_LANG = "en"
SUPPORTED = ("en", "pt")
LANG_NAMES = {"en": "English", "pt": "Português"}

_state = threading.local()


def set_language(lang):
    _state.lang = lang if lang in SUPPORTED else DEFAULT_LANG


def get_language():
    padrao = os.environ.get("APP_LANG", DEFAULT_LANG)
    if padrao not in SUPPORTED:
        padrao = DEFAULT_LANG
    return getattr(_state, "lang", padrao)


def t(key, /, **kwargs):
    """Texto traduzido. Cai para o inglês se faltar tradução, e devolve a própria
    chave se ela não existir — assim um texto esquecido aparece na tela em vez de
    quebrar a aplicação.

    A barra torna `key` posicional-only: sem isso, um texto com placeholder
    chamado {key} (como o Key ID na tela de configuração) colidiria com o
    parâmetro da própria função.
    """
    lang = get_language()
    texto = STRINGS.get(lang, {}).get(key) or STRINGS[DEFAULT_LANG].get(key) or key
    return texto.format(**kwargs) if kwargs else texto


STRINGS = {
    "en": {
        # ---------------------------------------------------------- sidebar --
        "sidebar.language": "Language",
        "sidebar.local_data": "Local data",
        "sidebar.no_credentials": "Credentials not configured.",
        "sidebar.go_to_settings": "Go to Settings",
        "sidebar.last_updated": "Last updated: {when}",
        "sidebar.no_data_yet": "No data collected yet.",
        "sidebar.refresh_button": "🔄 Refresh FortiCNAPP data",
        "sidebar.refreshing": "Querying the FortiCNAPP API… this can take 1–2 minutes.",
        "sidebar.refresh_ok": "Data updated.",
        "sidebar.refresh_fail": "Refresh failed. Details below.",
        "sidebar.period": "Period",
        "sidebar.period_label": "Analysis period",
        "period.last_7": "Last 7 days",
        "period.last_30": "Last 30 days",
        "period.last_90": "Last 90 days",
        "period.custom": "Custom",
        "period.range": "Date range",
        "period.data_starts": "⚠️ Data available from {date} (the API keeps {days} days).",
        "period.scope_note": "Applies to **alert** indicators. Vulnerabilities and coverage "
                             "reflect the latest collection{when}.",
        # -------------------------------------------------------------- home --
        "home.title": "🛡️ FortiCNAPP — Value Dashboard",
        "home.intro": """
This dashboard connects directly to your own FortiCNAPP account API and turns raw data into
indicators for two audiences:

- **Executive View** — for whoever decides: risk trend, response time, product utilization.
- **Security Operations** — the technical team's work queue: open alerts, vulnerabilities with
  known exploits, integration health.

Data is **stored locally** (`data/` folder) and never leaves your machine except to query the
FortiCNAPP API itself.
""",
        "home.need_credentials": "Before you start, register your FortiCNAPP API Key.",
        "home.need_data": "Credentials configured. Now use **Refresh data** in the sidebar for the "
                          "first collection.",
        "home.ready": "Data loaded. Use the left menu to navigate between dashboards.",
        # ------------------------------------------------------------ pages --
        "page.settings": "Settings",
        "page.executive": "Executive View",
        "page.operations": "Security Operations",
        "page.report": "Report",
        "page.home": "Home",
        # --------------------------------------------------------- settings --
        "settings.title": "⚙️ Settings",
        "settings.caption": "Register your FortiCNAPP API Key to connect this dashboard to your "
                            "account.",
        "settings.active": "Active credentials — source: **{source}**. Account: `{account}` · "
                           "Key ID: `{key}`",
        "settings.none": "No credentials configured yet. Fill in the form below.",
        "settings.source.env": "environment variables (set at deployment)",
        "settings.source.config_file": "file saved locally by this screen",
        "settings.source.legacy_root_file": "credentials file loose in the project root",
        "settings.env_notice": "Current credentials come from environment variables "
                               "(`FORTICNAPP_KEY_ID`, `FORTICNAPP_SECRET`, `FORTICNAPP_ACCOUNT`) "
                               "and take precedence over anything saved here. To use this screen, "
                               "remove those variables from the deployment.",
        "settings.where_expander": "Where do I find these?",
        "settings.where_body": """
1. In the FortiCNAPP console (URL like `https://YOURACCOUNT.lacework.net`), go to
   **Settings → API Keys**.
2. Create a key with read permission.
3. Download the generated `.json` (it holds `keyId`, `secret` and `account`). You can paste the
   whole file below, or fill in the three fields manually.
""",
        "settings.paste_toggle": "Paste the key JSON at once",
        "settings.paste_area": "Paste the contents of the API Key .json file here",
        "settings.json_needs_fields": "The JSON must contain keyId, secret and account.",
        "settings.json_invalid": "Invalid JSON — check that you pasted the complete file.",
        "settings.fill_all": "Fill in Account, Key ID and Secret before continuing.",
        "settings.test": "Test connection",
        "settings.save": "💾 Save",
        "settings.testing": "Authenticating with FortiCNAPP…",
        "settings.saved": "Credentials saved to `config/credentials.json` (outside the repository "
                          "and the image).",
        "settings.remove_expander": "Remove saved credentials",
        "settings.remove_warning": "This deletes config/credentials.json. Data already collected "
                                   "in data/ is not affected.",
        "settings.remove_button": "Remove saved credentials",
        # -------------------------------------------------------- executive --
        "exec.title": "📊 Executive View",
        "exec.caption": "Indicators for decision-making: risk, trend, response backlog and product "
                        "utilization.",
        "exec.no_alerts_in_period": "No alerts in the selected period ({period}).",
        "exec.headline": """
> #### In the analyzed period ({period}), FortiCNAPP raised **{total}** alerts —
> **{open_pct}%** ({open}) are still **open**, averaging **{age} days** old.
> The product is detecting; the bottleneck is in the response.
""",
        "exec.snapshot_row": "###### Current position — does not change with the selected period",
        "exec.vs_previous": "vs. previous period",
        "exec.trend_title": "Weekly alert trend",
        "exec.trend_help": "Alerts created per week, with the Critical/High line highlighted. "
                           "Shows whether exposure is growing, stable or falling over the period — "
                           "the trend reading a snapshot cannot give.",
        "exec.trend_empty": "Not enough data for a trend.",
        "exec.response_title": "Response time",
        "exec.response_help": "How long the team takes to handle what the product detects. Measures "
                              "the efficiency of the response process — not detection quality.",
        "exec.mttr_sample": " Sample: {n} closed alerts.",
        "exec.here": " Here: {value}.",
        "exec.how_to_read": "How to read these numbers",
        "exec.how_to_read_body": """
- **Resolution time (MTTR)** — measures the interval between an alert being opened and closed,
  considering only alerts already handled. It is shown as the **middle case** (median), not the
  average, so that a few extreme cases do not distort the reading.

- **Time to first response (MTTA) is not shown** — and that is a tool limitation, not an omission.
  It records only two moments: when the alert is born and when it is closed. There is no record of
  "someone picked this up", so any number here would be an estimate. Instead we show a verifiable
  figure: **how many alerts remain with no response at all** since they were created.

- **Time to detect (MTTD) is also not shown** — it would require knowing when the problem actually
  started, not just when it was detected. No tool in this category records that instant.
""",
        "exec.category_title": "Alerts by category",
        "exec.category_caption": "**Configuration** — misconfigurations in the cloud environment. "
                                 "**Behavior** and **Correlation** — activity outside the normal "
                                 "pattern observed inside the servers. These last two are the kind "
                                 "of detection that native cloud provider controls usually do not "
                                 "deliver.",
        "exec.vuln_by_sev_title": "Active vulnerabilities by severity",
        "exec.vuln_caption": "**{fixable}** of these flaws already have a vendor update available — "
                             "they only need the fix applied. **{exploited}** already have a "
                             "ready-made attack tool, and **{wormable}** can spread by themselves "
                             "between servers.",
        "exec.coverage_title": "Breadth of visibility (what the product is watching)",
        "exec.coverage_help": "Volume of entities FortiCNAPP continuously inventories and monitors — "
                              "visibility that would normally require several native tools to "
                              "rebuild by hand.",
        "exec.coverage_caption": "An inventory the product keeps up to date on its own, "
                                 "continuously. Rebuilding that same map manually, or with each "
                                 "cloud provider's native controls, would take several tools and "
                                 "recurring effort from the team.",
        "exec.contract_title": "Contract utilization",
        "exec.contract_help": "How much of what was contracted is actually in use (e.g. agent "
                              "licenses used vs. purchased). Shown only when the API returns a "
                              "valid contracted total for the item.",
        "exec.contract_line": "**{name}** — {used} of {purchased} contracted in use",
        # ------------------------------------------------------- operations --
        "ops.title": "🛠️ Security Operations",
        "ops.caption": "Work queue: what to prioritize now.",
        "ops.types_title": "Most frequent alert types — {period}",
        "ops.top_hosts_empty": "No vulnerability data.",
        "ops.cloud_health_title": "Cloud integration health",
        "ops.cloud_col_name": "Name",
        "ops.cloud_col_status": "Status",
        "ops.cloud_col_last": "Last successful collection",
        "ops.cloud_ok": "OK",
        "ops.cloud_fail": "⚠️ Failing",
        "ops.cloud_empty": "No cloud account cached.",
        "ops.known_exploited_title": "Vulnerabilities with known exploits (prioritize first)",
        "ops.known_exploited_empty": "No flaw with an available attack tool or confirmed malware "
                                     "use was found in the latest collection.",
        "ops.open_alerts_title": "Open alerts",
        "ops.filter_severity": "Filter by severity",
        "ops.open_alerts_count": "{shown} open alerts (out of {total} total).",
        "ops.open_alerts_empty": "No open alerts in the collected period.",
        "ops.hover_type": "type",
        "ops.hover_count": "occurrences",
        # ----------------------------------------------------------- report --
        "report.page_title": "🖨️ Report",
        "report.page_caption": "Builds a single document, ready to print or save as PDF (use the "
                               "button below, or Ctrl+P / Cmd+P).",
        "report.period_applied": "Period applied to alert indicators: **{period}** (adjust in the "
                                 "sidebar).",
        "report.client_name": "Client/account name (appears in the report header)",
        "report.client_placeholder": "e.g.: Security Posture — [Client Name]",
        "report.include_ops": "Include operational annex",
        "report.include_ops_help": "Adds tables of open critical/high alerts and the most "
                                   "vulnerable servers.",
        "report.include_glossary": "Include glossary",
        "report.include_glossary_help": "Adds the definition of each indicator at the end — the "
                                        "same explanations as the tooltips, which do not appear in "
                                        "the printed version.",
        "report.print_button": "🖨️ Print / Save as PDF",
        "report.no_data": "No data collected yet. Use **Refresh data** in the sidebar.",
        # ------------------------------------------- report document content --
        "doc.brand": "🛡️ FortiCNAPP — Value Dashboard",
        "doc.default_title": "Security posture report",
        "doc.generated_at": "Generated on {when}",
        "doc.period": "Period analyzed: {period}",
        "doc.footer": "Generated automatically by the FortiCNAPP Value Dashboard on {when}. "
                      "Data collected directly from your own FortiCNAPP account API.",
        "doc.no_data": "No data.",
        "doc.section.executive": "Executive summary",
        "doc.section.response": "Response time",
        "doc.section.vulns": "Active vulnerabilities",
        "doc.section.detecting": "What the product has been detecting",
        "doc.section.coverage": "Coverage and visibility",
        "doc.section.annex": "Operational annex",
        "doc.section.glossary": "Indicator glossary",
        "doc.headline": "In the analyzed period, FortiCNAPP raised <b>{total}</b> alerts for this "
                        "account — <b>{open_pct}%</b> ({open}) are still <b>open</b>, averaging "
                        "<b>{age} days</b> old. The product is detecting; the bottleneck is in the "
                        "response.",
        "doc.kpi.alerts_period": "Alerts (period)",
        "doc.kpi.sample_of": "sample of {n}",
        "doc.kpi.open_no_touch": "Open with no response",
        "doc.kpi.of_total": "{part} of {total}",
        "doc.kpi.attack_tool": "attack tool already available",
        "doc.kpi.total_active": "Total active flaws",
        "doc.kpi.all_severities": "all severities",
        "doc.kpi.integrations": "{n} integrations configured",
        "doc.block.mttr_by_sev": "Resolution time by severity",
        "doc.block.severity_dist": "Distribution by severity",
        "doc.block.top_exploited": "Top priority — flaws with an available attack tool (top 10)",
        "doc.block.alert_types": "Most frequent alert types in the period",
        "doc.block.open_alerts": "Highest-severity alerts still open",
        "doc.block.open_alerts_capped": " (the {n} oldest, out of {total})",
        "doc.block.open_alerts_all": " ({n} in total, oldest first)",
        "doc.block.top_hosts": "Servers with the most vulnerabilities (top 10)",
        "doc.col.severity": "Severity",
        "doc.col.mttr_days": "Median resolution time (days)",
        "doc.col.server": "Server",
        "doc.col.cve": "CVE",
        "doc.col.cvss": "CVSS",
        "doc.col.fix_available": "Fix available",
        "doc.col.alert": "Alert",
        "doc.col.source": "Source",
        "doc.col.idle_days": "Idle for (days)",
        "doc.col.critical": "Critical",
        "doc.col.high": "High",
        "doc.col.total": "Total",
        "doc.col.detected": "What was detected",
        "doc.col.occurrences": "Occurrences",
        "doc.col.pct_total": "% of total",
        "doc.yes": "Yes",
        "doc.no": "No",
        "doc.note.cvss": "CVSS is the flaw's severity score, from 0 to 10, defined by the "
                         "international standard. Scores from 9.0 up are considered critical.",
        "doc.note.how_to_read": "<b>How to read:</b> resolution time considers the interval between "
                                "opening and closing each alert already handled. Time to first "
                                "response is not shown because the tool records only when the alert "
                                "is born and when it is closed, without marking the moment someone "
                                "picked it up. Instead of estimating that, we show a verifiable "
                                "figure above: how many alerts remain with no response at all.",
        "doc.note.period_warning": "<b>Mind the period:</b> ",
        "doc.note.snapshot_vulns": "<b>Current position:</b> unlike the alerts, this section does "
                                   "not refer to the analyzed period — it shows the flaws that "
                                   "exist in the environment today, as of the {when} collection.",
        "doc.note.snapshot_coverage": "Also the current position of the environment, not of the "
                                      "analyzed period.",
        "doc.note.alert_types": "<b>How to read:</b> this is the plain-language translation of the "
                                "alert types that repeated the most. High concentration in a few "
                                "types usually points to a rule that needs tuning — not a real "
                                "increase in risk. Here, the three most frequent types account for "
                                "<b>{pct}%</b> of all alerts in the period: cutting that noise "
                                "frees the team to handle what actually matters.",
        # ---------------------------------------------------- bias / limits --
        "unit.days": "days",
        "conn.ok": "Connection authenticated successfully.",
        "conn.unreachable": "Could not connect to https://{account}: {error}",
        "conn.auth_failed": "Authentication failed (HTTP {status}): {body}",
        "bias.no_sample": "No alert created in this period has been closed yet, so there is no "
                          "resolution time to calculate. Choose a longer period to assess response.",
        "bias.short_period": "Short periods distort response indicators: alerts created a few days "
                             "ago have not had time to be handled, which inflates the open "
                             "percentage and artificially lowers resolution time. To assess "
                             "response capability, prefer the {days}-day period.",
    },
    "pt": {
        # ---------------------------------------------------------- sidebar --
        "sidebar.language": "Idioma",
        "sidebar.local_data": "Dados locais",
        "sidebar.no_credentials": "Credenciais não configuradas.",
        "sidebar.go_to_settings": "Ir para Configuração",
        "sidebar.last_updated": "Última atualização: {when}",
        "sidebar.no_data_yet": "Nenhum dado coletado ainda.",
        "sidebar.refresh_button": "🔄 Atualizar dados do FortiCNAPP",
        "sidebar.refreshing": "Consultando a API do FortiCNAPP… isso pode levar 1–2 minutos.",
        "sidebar.refresh_ok": "Dados atualizados.",
        "sidebar.refresh_fail": "Falha ao atualizar. Veja os detalhes abaixo.",
        "sidebar.period": "Período",
        "sidebar.period_label": "Período analisado",
        "period.last_7": "Últimos 7 dias",
        "period.last_30": "Últimos 30 dias",
        "period.last_90": "Últimos 90 dias",
        "period.custom": "Personalizado",
        "period.range": "Intervalo",
        "period.data_starts": "⚠️ Há dados a partir de {date} (a API mantém {days} dias).",
        "period.scope_note": "Recorta os indicadores de **alertas**. Vulnerabilidades e cobertura "
                             "refletem a coleta mais recente{when}.",
        # -------------------------------------------------------------- home --
        "home.title": "🛡️ FortiCNAPP — Painel de Valor",
        "home.intro": """
Este painel conecta diretamente à API do FortiCNAPP da sua conta e traduz os dados brutos
em indicadores para dois públicos:

- **Visão Gerencial** — indicadores para o decisor de segurança/tecnologia.
- **Operações de Segurança** — fila de trabalho do time técnico: alertas em aberto,
  vulnerabilidades com exploit conhecido, saúde das integrações.

Os dados ficam **armazenados localmente** (pasta `data/`) e só saem da sua máquina para consultar
a própria API do FortiCNAPP.
""",
        "home.need_credentials": "Antes de começar, cadastre sua API Key do FortiCNAPP.",
        "home.need_data": "Credenciais configuradas. Agora use **Atualizar dados** na barra lateral "
                          "para a primeira coleta.",
        "home.ready": "Dados carregados. Use o menu à esquerda para navegar entre os dashboards.",
        # ------------------------------------------------------------ pages --
        "page.settings": "Configuração",
        "page.executive": "Visão Gerencial",
        "page.operations": "Operações de Segurança",
        "page.report": "Relatório",
        "page.home": "Início",
        # --------------------------------------------------------- settings --
        "settings.title": "⚙️ Configuração",
        "settings.caption": "Cadastre a API Key do FortiCNAPP para conectar este painel à sua conta.",
        "settings.active": "Credenciais ativas — origem: **{source}**. Conta: `{account}` · "
                           "Key ID: `{key}`",
        "settings.none": "Nenhuma credencial configurada ainda. Preencha o formulário abaixo.",
        "settings.source.env": "variáveis de ambiente (definidas na implantação)",
        "settings.source.config_file": "arquivo salvo localmente por esta tela",
        "settings.source.legacy_root_file": "arquivo de credenciais solto na raiz do projeto",
        "settings.env_notice": "As credenciais atuais vêm de variáveis de ambiente "
                               "(`FORTICNAPP_KEY_ID`, `FORTICNAPP_SECRET`, `FORTICNAPP_ACCOUNT`) "
                               "e têm prioridade sobre o que for salvo aqui. Para usar esta tela, "
                               "remova essas variáveis da implantação.",
        "settings.where_expander": "Onde encontro esses dados?",
        "settings.where_body": """
1. No console do FortiCNAPP (URL no formato `https://SUACONTA.lacework.net`), vá em
   **Settings → API Keys**.
2. Crie uma chave com permissão de leitura.
3. Baixe o `.json` gerado (contém `keyId`, `secret` e `account`). Você pode colar o arquivo
   inteiro abaixo, ou preencher os três campos manualmente.
""",
        "settings.paste_toggle": "Colar o JSON da chave de uma vez",
        "settings.paste_area": "Cole aqui o conteúdo do arquivo .json da API Key",
        "settings.json_needs_fields": "O JSON precisa conter keyId, secret e account.",
        "settings.json_invalid": "JSON inválido — confira se colou o arquivo completo.",
        "settings.fill_all": "Preencha Account, Key ID e Secret antes de continuar.",
        "settings.test": "Testar conexão",
        "settings.save": "💾 Salvar",
        "settings.testing": "Autenticando no FortiCNAPP…",
        "settings.saved": "Credenciais salvas em `config/credentials.json` (fora do repositório e "
                          "da imagem).",
        "settings.remove_expander": "Remover credenciais salvas",
        "settings.remove_warning": "Isso apaga config/credentials.json. Os dados já coletados em "
                                   "data/ não são afetados.",
        "settings.remove_button": "Remover credenciais salvas",
        # -------------------------------------------------------- executive --
        "exec.title": "📊 Visão Gerencial",
        "exec.caption": "Indicadores para decisão: risco, tendência, backlog de resposta e "
                        "utilização do produto.",
        "exec.no_alerts_in_period": "Nenhum alerta no período selecionado ({period}).",
        "exec.headline": """
> #### No período analisado ({period}), o FortiCNAPP gerou **{total}** alertas —
> **{open_pct}%** ({open}) ainda estão **em aberto**, com idade média de **{age} dias**.
> O produto está detectando; o gargalo está na resposta.
""",
        "exec.snapshot_row": "###### Posição atual — não muda com o período selecionado",
        "exec.vs_previous": "vs. período anterior",
        "exec.trend_title": "Tendência semanal de alertas",
        "exec.trend_help": "Volume de alertas criados por semana, com a linha de Críticos/Altos "
                           "destacada. Mostra se a exposição está crescendo, estável ou caindo ao "
                           "longo do período — a leitura de tendência que um retrato do momento "
                           "não dá.",
        "exec.trend_empty": "Sem dados suficientes para tendência.",
        "exec.response_title": "Tempo de resposta",
        "exec.response_help": "Quanto tempo o time leva para tratar o que o produto detecta. Mede a "
                              "eficiência do processo de resposta — não a qualidade da detecção.",
        "exec.mttr_sample": " Amostra: {n} alertas fechados.",
        "exec.here": " Nesta conta: {value}.",
        "exec.how_to_read": "Como ler estes números",
        "exec.how_to_read_body": """
- **Tempo de resolução (MTTR)** — mede o intervalo entre a abertura de um alerta e o seu
  encerramento, considerando apenas os alertas já tratados. É apresentado como o **caso do meio**
  (mediana), e não como média, para que poucos casos extremos não distorçam a leitura.

- **Tempo até o primeiro atendimento (MTTA) não é apresentado** — e isso é uma limitação da
  ferramenta, não uma omissão. Ela registra apenas dois momentos: quando o alerta nasce e quando é
  encerrado. Não existe um registro de "alguém assumiu este alerta", então qualquer número aqui
  seria estimativa. No lugar, mostramos um dado verificável: **quantos alertas seguem sem nenhum
  atendimento** desde que foram criados.

- **Tempo até a detecção (MTTD) também não é apresentado** — exigiria saber quando o problema
  realmente começou, e não apenas quando foi detectado. Esse instante não é registrado por nenhuma
  ferramenta desta categoria.
""",
        "exec.category_title": "Alertas por categoria",
        "exec.category_caption": "**Configuração** — erros de configuração no ambiente de nuvem. "
                                 "**Comportamento** e **Correlação** — atividade fora do padrão "
                                 "observada dentro dos servidores. Estes dois últimos são o tipo de "
                                 "detecção que os controles nativos dos provedores de nuvem "
                                 "normalmente não entregam.",
        "exec.vuln_by_sev_title": "Vulnerabilidades ativas por severidade",
        "exec.vuln_caption": "**{fixable}** dessas falhas já têm atualização disponível do "
                             "fabricante — dependem apenas de aplicar a correção. **{exploited}** "
                             "já possuem ferramenta de ataque pronta e disponível, e **{wormable}** "
                             "conseguem se espalhar sozinhas entre servidores.",
        "exec.coverage_title": "Amplitude de visibilidade (o que o produto está observando)",
        "exec.coverage_help": "Volume de entidades que o FortiCNAPP inventaria e monitora "
                              "continuamente — visibilidade que normalmente exigiria múltiplas "
                              "ferramentas nativas para reconstruir manualmente.",
        "exec.coverage_caption": "Inventário que o produto mantém atualizado sozinho, de forma "
                                 "contínua. Reconstruir esse mesmo mapa manualmente, ou com os "
                                 "controles nativos de cada provedor de nuvem, exigiria várias "
                                 "ferramentas e trabalho recorrente da equipe.",
        "exec.contract_title": "Utilização do contrato",
        "exec.contract_help": "Quanto do que foi contratado está efetivamente em uso (ex.: licenças "
                              "de agente usadas vs. adquiridas). Só é exibido quando a API retorna "
                              "um total contratado válido para o item.",
        "exec.contract_line": "**{name}** — usados {used} de {purchased} contratados",
        # ------------------------------------------------------- operations --
        "ops.title": "🛠️ Operações de Segurança",
        "ops.caption": "Fila de trabalho: o que priorizar agora.",
        "ops.types_title": "Tipos de alerta mais frequentes — {period}",
        "ops.top_hosts_empty": "Sem dados de vulnerabilidades.",
        "ops.cloud_health_title": "Saúde das integrações cloud",
        "ops.cloud_col_name": "Nome",
        "ops.cloud_col_status": "Status",
        "ops.cloud_col_last": "Última coleta OK",
        "ops.cloud_ok": "OK",
        "ops.cloud_fail": "⚠️ Falha",
        "ops.cloud_empty": "Nenhuma conta cloud cacheada.",
        "ops.known_exploited_title": "Vulnerabilidades com exploit conhecido (priorizar primeiro)",
        "ops.known_exploited_empty": "Nenhuma falha com ferramenta de ataque disponível ou uso "
                                     "confirmado por malware foi identificada na última coleta.",
        "ops.open_alerts_title": "Alertas em aberto",
        "ops.filter_severity": "Filtrar por severidade",
        "ops.open_alerts_count": "{shown} alertas em aberto (de {total} no total).",
        "ops.open_alerts_empty": "Nenhum alerta em aberto no período coletado.",
        "ops.hover_type": "tipo",
        "ops.hover_count": "ocorrências",
        # ----------------------------------------------------------- report --
        "report.page_title": "🖨️ Relatório",
        "report.page_caption": "Monta um relatório único, pronto para impressão ou para salvar como "
                               "PDF (use o botão abaixo ou Ctrl+P / Cmd+P).",
        "report.period_applied": "Período aplicado aos indicadores de alertas: **{period}** "
                                 "(ajuste na barra lateral).",
        "report.client_name": "Nome do cliente/conta (aparece no cabeçalho do relatório)",
        "report.client_placeholder": "Ex.: Postura de Segurança — [Nome do Cliente]",
        "report.include_ops": "Incluir anexo operacional",
        "report.include_ops_help": "Adiciona tabelas de alertas críticos/altos em aberto e top "
                                   "servidores vulneráveis.",
        "report.include_glossary": "Incluir glossário",
        "report.include_glossary_help": "Adiciona ao final a definição de cada indicador — as "
                                        "mesmas explicações dos tooltips, que não aparecem na "
                                        "versão impressa.",
        "report.print_button": "🖨️ Imprimir / Salvar como PDF",
        "report.no_data": "Nenhum dado coletado ainda. Use **Atualizar dados** na barra lateral.",
        # ------------------------------------------- report document content --
        "doc.brand": "🛡️ FortiCNAPP — Painel de Valor",
        "doc.default_title": "Relatório de postura de segurança",
        "doc.generated_at": "Gerado em {when}",
        "doc.period": "Período analisado: {period}",
        "doc.footer": "Gerado automaticamente pelo FortiCNAPP Painel de Valor em {when}. "
                      "Dados coletados diretamente da API do FortiCNAPP da própria conta.",
        "doc.no_data": "Sem dados.",
        "doc.section.executive": "Resumo executivo",
        "doc.section.response": "Tempo de resposta",
        "doc.section.vulns": "Vulnerabilidades ativas",
        "doc.section.detecting": "O que o produto vem detectando",
        "doc.section.coverage": "Cobertura e visibilidade",
        "doc.section.annex": "Anexo operacional",
        "doc.section.glossary": "Glossário dos indicadores",
        "doc.headline": "No período analisado, o FortiCNAPP gerou <b>{total}</b> alertas para esta "
                        "conta — <b>{open_pct}%</b> ({open}) ainda estão <b>em aberto</b>, com "
                        "idade média de <b>{age} dias</b>. O produto está detectando; o gargalo "
                        "está na resposta.",
        "doc.kpi.alerts_period": "Alertas (período)",
        "doc.kpi.sample_of": "amostra de {n}",
        "doc.kpi.open_no_touch": "Abertos sem interação",
        "doc.kpi.of_total": "{part} de {total}",
        "doc.kpi.attack_tool": "ferramenta de ataque já disponível",
        "doc.kpi.total_active": "Total de falhas ativas",
        "doc.kpi.all_severities": "todas as gravidades",
        "doc.kpi.integrations": "{n} integrações configuradas",
        "doc.block.mttr_by_sev": "Tempo de resolução por gravidade",
        "doc.block.severity_dist": "Distribuição por gravidade",
        "doc.block.top_exploited": "Prioridade máxima — falhas com ferramenta de ataque disponível "
                                   "(top 10)",
        "doc.block.alert_types": "Tipos de alerta mais frequentes no período",
        "doc.block.open_alerts": "Alertas de maior gravidade ainda em aberto",
        "doc.block.open_alerts_capped": " (os {n} mais antigos, de {total})",
        "doc.block.open_alerts_all": " ({n} no total, do mais antigo ao mais recente)",
        "doc.block.top_hosts": "Servidores com mais vulnerabilidades (10 primeiros)",
        "doc.col.severity": "Gravidade",
        "doc.col.mttr_days": "Tempo mediano de resolução (dias)",
        "doc.col.server": "Servidor",
        "doc.col.cve": "CVE",
        "doc.col.cvss": "CVSS",
        "doc.col.fix_available": "Correção disponível",
        "doc.col.alert": "Alerta",
        "doc.col.source": "Origem",
        "doc.col.idle_days": "Parado há (dias)",
        "doc.col.critical": "Críticas",
        "doc.col.high": "Altas",
        "doc.col.total": "Total",
        "doc.col.detected": "O que foi detectado",
        "doc.col.occurrences": "Ocorrências",
        "doc.col.pct_total": "% do total",
        "doc.yes": "Sim",
        "doc.no": "Não",
        "doc.note.cvss": "CVSS é a nota de gravidade da falha, de 0 a 10, definida pelo padrão "
                         "internacional. Notas a partir de 9,0 são consideradas críticas.",
        "doc.note.how_to_read": "<b>Como ler:</b> o tempo de resolução considera o intervalo entre "
                                "a abertura e o encerramento de cada alerta já tratado. O tempo até "
                                "o primeiro atendimento não é apresentado porque a ferramenta "
                                "registra apenas quando o alerta nasce e quando é encerrado, sem "
                                "marcar o momento em que alguém o assumiu. Em vez de estimar esse "
                                "valor, apresentamos acima um dado verificável: quantos alertas "
                                "seguem sem qualquer atendimento.",
        "doc.note.period_warning": "<b>Atenção ao período:</b> ",
        "doc.note.snapshot_vulns": "<b>Posição atual:</b> diferentemente dos alertas, esta seção "
                                   "não se refere ao período analisado — mostra as falhas que "
                                   "existem hoje no ambiente, conforme a coleta de {when}.",
        "doc.note.snapshot_coverage": "Também é a posição atual do ambiente, não do período "
                                      "analisado.",
        "doc.note.alert_types": "<b>Como ler:</b> esta é a tradução, em linguagem comum, dos tipos "
                                "de alerta que mais se repetiram. Concentração alta em poucos tipos "
                                "normalmente indica regra que precisa de ajuste — e não aumento "
                                "real de risco. Aqui, os três tipos mais frequentes respondem por "
                                "<b>{pct}%</b> de todos os alertas do período: reduzir esse ruído "
                                "libera a equipe para tratar o que de fato importa.",
        # ---------------------------------------------------- bias / limits --
        "unit.days": "dias",
        "conn.ok": "Conexão autenticada com sucesso.",
        "conn.unreachable": "Não foi possível conectar em https://{account}: {error}",
        "conn.auth_failed": "Falha na autenticação (HTTP {status}): {body}",
        "bias.no_sample": "Nenhum alerta criado neste período foi encerrado até agora, então não há "
                          "tempo de resolução a calcular. Escolha um período maior para avaliar a "
                          "resposta.",
        "bias.short_period": "Períodos curtos distorcem os indicadores de resposta: alertas criados "
                             "há poucos dias ainda não tiveram tempo de ser tratados, o que infla o "
                             "percentual em aberto e reduz artificialmente o tempo de resolução. "
                             "Para avaliar a capacidade de resposta, prefira o período de {days} "
                             "dias.",
    },
}
