# FortiCNAPP — Value Dashboard

*[Versão em português](README.pt-BR.md)*

Connects to your own FortiCNAPP (Lacework v2) account API, caches the data **locally** (`data/`
folder — it never leaves your machine) and turns it into indicators for two audiences:

- **Executive View** — for whoever decides: risk trend, response time (MTTR), product utilization.
- **Security Operations** — the technical team's work queue: open alerts, vulnerabilities with
  known exploits, integration health.
- **Report** — consolidates the indicators into a professional layout, ready to print or save as
  PDF (native browser printing), with a customizable client name.

Available in **English and Portuguese** — switch from the sidebar at any time.

API credentials also stay on your machine only (`config/` folder — never committed, never sent
anywhere other than the FortiCNAPP API itself).

## Examples

> The images below were generated with **demo mode** on: server, user, domain and integration
> names are pseudonymized. The numbers, severities and CVEs are real — what you see is exactly
> what the dashboard produces.

### Executive View

![Executive View](docs/screenshots/executive-view.png)

### Security Operations

![Security Operations](docs/screenshots/security-operations.png)

### Printable report

![Report](docs/screenshots/report.png)

## Running it

First, clone the repository:

```bash
git clone https://github.com/Jamsux/forticnapp-painel-de-valor.git
cd forticnapp-painel-de-valor
```

### Option 1 — Docker (recommended, identical on Windows, macOS and Linux)

```bash
docker compose up --build
```

Open [http://localhost:8501](http://localhost:8501), go to **⚙️ Settings** and paste your
FortiCNAPP API Key. Data and configuration persist in the host's `data/` and `config/` folders
(mounted as volumes), so they survive container restarts.

On Windows, just install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and run
the command above in PowerShell.

### Option 2 — Local Python (macOS / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run dashboard/Home.py
```

### Option 3 — Local Python (Windows / PowerShell)

Requires [Python 3.10+](https://www.python.org/downloads/) — tick **"Add Python to PATH"** during
installation.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

streamlit run dashboard/Home.py
```

> If PowerShell blocks the virtual environment activation, allow scripts for your user:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

On Windows, use `python` instead of `python3` in the other commands in this README
(e.g. `python scripts\refresh_data.py`).

With any option, open [http://localhost:8501](http://localhost:8501) and register your API Key
under **⚙️ Settings**.

## Language

The sidebar has a language selector (**English / Português**) that applies to the whole
application, including the printed report. English is the default.

To change the default, set the `APP_LANG` environment variable (`en` or `pt`), or pass `--lang`
to the export script.

## Getting the FortiCNAPP API Key

1. In the FortiCNAPP console (`https://YOURACCOUNT.lacework.net`), go to **Settings → API Keys**.
2. Create a key with read permission.
3. Download the generated `.json` (it holds `keyId`, `secret`, `account`) and paste it into the
   dashboard's Settings screen — or fill in the three fields manually.

For automated environments, set the `FORTICNAPP_KEY_ID`, `FORTICNAPP_SECRET` and
`FORTICNAPP_ACCOUNT` environment variables instead (see `.env.example`). They take precedence over
anything saved through the Settings screen.

## Analysis period

The sidebar has a period selector: **7 / 30 / 90 days** or a **custom range**. The choice applies
to every page and to the printed report.

Two important notes:

- **The period slices the alert indicators** (volume, trend, MTTR, alert types, open queue).
  **Vulnerabilities and coverage are the current snapshot** of the environment — the product does
  not keep "June's vulnerabilities", it keeps today's state. This is flagged on screen and in the
  report.
- **The limit is 90 days**, imposed by the API itself (`startTime has to be within the past 90
  Days`). Since the collection already fetches the whole window, switching periods is instant — no
  new queries.

**Careful with short periods:** the slice is by alert creation date, so in a short window only the
alerts that were both created and closed inside it count as "resolved". That inflates "% open" and
artificially lowers resolution time (in the last 7 days of the sample account there are *zero*
closed alerts, and MTTR would read "0 days"). The dashboard detects this case, shows "—" instead of
a misleading number, and displays a warning. To assess response capability, use 90 days.

From the command line:

```bash
python3 scripts/export_report.py --out report.pdf --pdf --days 30
python3 scripts/export_report.py --out report.pdf --pdf --from 2026-06-01 --to 2026-06-30
```

## Refreshing the data

- From the dashboard: the **"🔄 Refresh FortiCNAPP data"** button in the sidebar.
- From the terminal: `python3 scripts/refresh_data.py` (inside the venv) — handy for scheduling
  with cron.

## Indicator explanations

Every indicator has a tooltip (the **?** icon) explaining what it means and how it is calculated.
The definitions live in [`src/glossary.py`](src/glossary.py) — a single source of truth shared by
the dashboards and the report, so the same number is never explained two different ways. Since
tooltips do not exist on paper, the printed report includes the same definitions in a **Indicator
glossary** section at the end (which can be turned off).

## Printable report

The **🖨️ Report** page builds a single document (header with client name, executive summary,
response time, vulnerabilities, coverage and an optional operational annex) with a report layout —
not a screenshot of the dashboard. Click **"Print / Save as PDF"** (or use Ctrl+P / Cmd+P): the
sidebar and the page's own controls disappear from the printed/PDF version, leaving only the
report.

The print CSS handles pagination: breaks only between blocks (never inside a card, table row or
definition), table headers repeated on each page, colors preserved on paper, and Streamlit's
scrolling containers converted to normal flow — without that, the browser clips everything past
the first page.

### Generating the report without opening the dashboard

```bash
python3 scripts/export_report.py --out report.pdf --pdf --client-name "Client Name" --lang en
```

Produces self-contained HTML (default) or PDF (`--pdf`, via headless Chrome/Chromium). It uses
exactly the same assembly function as the dashboard page
(`src/report.build_report_html`), so the result is identical — useful for scheduling a periodic PDF.

## What is collected

- **Alerts** (last 90 days, all pages) — covers CSPM (`Policy` category), anomalous behavior
  (`Anomaly`) and composite detections (`Composite`).
- **Active host vulnerabilities** — counts by severity plus Critical/High detail (deduplicated by
  host+CVE), including public exploit / known malware flags.
- **Inventory** — monitored servers, connected cloud accounts and their health, visibility counts
  (users, applications, packages, network interfaces).
- **Rules/contract** — `AlertRules`, `ReportRules`, `ResourceGroups`.

## Response time indicators (MTTR / MTTA / MTTD)

The Executive View shows a real **MTTR** (Mean Time to Resolve), computed from
`lastUserUpdatedTime − startTime` for alerts with `status = Closed` — median and p90, overall and
by severity, with the formula explained in an expander on the page itself.

**MTTA and MTTD are not reported** because the API does not support that calculation: there is no
"acknowledged" event distinct from "closed" in the `Alerts/search` data, and the per-alert
detail/history endpoints (`/Alerts/{id}`, `/Alerts/{id}/Timeline`) returned 400/500 errors in
testing. Rather than estimating those numbers, the dashboard shows an equivalent real figure: the
share of currently open alerts with no recorded interaction since creation — a more honest signal
of the response gap than an approximate MTTA.

## Known API limitations

- The `Configs/ComplianceEvaluations/search` endpoint did not respond to any request body tested
  (generic "Invalid request", even with valid `timeFilter`/`filters`) — the full documentation sits
  behind a login at fndn.fortinet.net. As a workaround, the CSPM/compliance indicator comes from
  the `Policy` category inside `Alerts`, which already reflects real misconfiguration findings.
- No dedicated v2 endpoint for **CIEM** (identity entitlements) was found — the module may not be
  enabled on the tested account, or it may use a different API path.
- `GET /api/v2/ContractInfo` was unstable (intermittent 500) during testing — the collection script
  does not fail in that case, it simply skips that data.

## Demo mode (for screenshots and presentations)

To show the dashboard without exposing environment identifiers, run it with `FORTICNAPP_DEMO=1`:

```bash
FORTICNAPP_DEMO=1 streamlit run dashboard/Home.py
```

In this mode the data is pseudonymized as it loads: server names (including where they are quoted
inside alert descriptions), user accounts and domain, cloud integration names and e-mails.
**Counts, severities, CVEs and dates stay intact** — and cloud account identifiers get stable
pseudonyms, so "one account with two integrations" is still counted as one account.

The images in this README were generated with:

```bash
python3 scripts/capture_screenshots.py
```

## Project structure

```
dashboard/           # Streamlit app (entry point + views)
src/                 # API client, collectors, aggregation, i18n, report
scripts/             # data refresh, report export, screenshot capture
config/              # credentials (gitignored, created at runtime)
data/                # local cache of collected data (gitignored, created at runtime)
```

## Security

- No credentials are ever committed: `config/` and any `*.json` are in `.gitignore` and
  `.dockerignore`.
- Collected data (`data/`) also never leaves the machine where the dashboard runs.
- The API Key only needs **read** permission.

## License

Apache 2.0 — see [LICENSE](LICENSE).
