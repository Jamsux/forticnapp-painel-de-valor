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


# A API devolve as severidades em inglês (Critical/High/...). Os VALORES seguem
# em inglês em filtros e comparações — o que muda é só a exibição, para o
# analista continuar cruzando com o console do FortiCNAPP sem descompasso.
SEVERITY_LABELS = {
    "en": {"Critical": "Critical", "High": "High", "Medium": "Medium",
           "Low": "Low", "Info": "Info"},
    "pt": {"Critical": "Crítica", "High": "Alta", "Medium": "Média",
           "Low": "Baixa", "Info": "Informativa"},
}


def severity_label(value):
    from .i18n import DEFAULT_LANG, get_language
    mapa = SEVERITY_LABELS.get(get_language(), SEVERITY_LABELS[DEFAULT_LANG])
    return mapa.get(value, value or "—")


SEVERITY_COLOR_MAP = {
    "Critical": PALETTE["critical"],
    "High": PALETTE["high"],
    "Medium": PALETTE["medium"],
    "Low": PALETTE["low"],
    "Info": PALETTE["info"],
}
