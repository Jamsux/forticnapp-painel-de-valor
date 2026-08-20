"""Paleta de cores compartilhada entre os dashboards e o relatório para impressão."""

PALETTE = {
    "critical": "#B3261E",
    "high": "#E8590C",
    "medium": "#C77700",
    "low": "#5A7D4C",
    "info": "#6B7280",
    "accent": "#2563EB",
    "ink": "#0F172A",
    "muted": "#64748B",
    "border": "#E2E8F0",
}

# A API classifica os alertas em Policy/Anomaly/Composite. Traduzido para termos
# que dizem o que a categoria significa, já que o relatório vai para a diretoria.
CATEGORY_LABELS = {
    "en": {"Policy": "Configuration", "Anomaly": "Behavior", "Composite": "Correlation"},
    "pt": {"Policy": "Configuração", "Anomaly": "Comportamento", "Composite": "Correlação"},
}


def category_label(value):
    from .i18n import DEFAULT_LANG, get_language
    mapa = CATEGORY_LABELS.get(get_language(), CATEGORY_LABELS[DEFAULT_LANG])
    return mapa.get(value, value or "—")


SEVERITY_COLOR_MAP = {
    "Critical": PALETTE["critical"],
    "High": PALETTE["high"],
    "Medium": PALETTE["medium"],
    "Low": PALETTE["low"],
    "Info": PALETTE["info"],
}
