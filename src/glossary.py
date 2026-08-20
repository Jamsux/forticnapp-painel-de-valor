"""Definições dos indicadores — fonte única de verdade, em inglês e português.

Usado como tooltip (`help=`) nos dashboards, como `title=` nos cards do relatório
e para montar o glossário impresso. Manter as definições aqui evita que dashboard
e relatório expliquem o mesmo número de formas diferentes.

Linguagem: o público é o decisor (CISO/diretoria), não o analista. Cada definição
diz o que o número significa e por que importa — sem nomes de campo, sem jargão
de API e sem fórmula. A precisão é mantida: quando a contagem tem uma regra que
muda a leitura (ex.: o mesmo problema contado uma vez por servidor), isso é dito
em linguagem clara.

Estrutura: GLOSSARY[idioma][chave] = (rótulo curto, definição).
"""
from .i18n import DEFAULT_LANG, get_language

GLOSSARY = {
    "en": {
        # ----------------------------------------------------------- Alerts --
        "alerts_total": (
            "Alerts (90 days)",
            "How many risks the tool identified and flagged in the period. Covers three fronts: "
            "misconfigurations in the cloud environment, behavior outside the normal pattern "
            "observed inside the servers, and threats identified by correlating several signals.",
        ),
        "alerts_open_pct": (
            "% open",
            "How much of what was detected has not been handled yet. It is the thermometer of "
            "response capacity: the higher it is, the more already-identified risk sits with "
            "nobody acting on it.",
        ),
        "alerts_critical_high_open": (
            "Critical/High open",
            "Highest-severity alerts still untreated. This is the queue that should be handled "
            "as a priority and has not been.",
        ),
        "alerts_avg_age": (
            "Average age (open)",
            "How long, on average, untreated alerts have been sitting. Tells a recent, one-off "
            "backlog apart from a chronic process problem.",
        ),
        "alerts_last_7d": (
            "Alerts last 7d",
            "Volume of new detections in the last week, compared with the previous week. Shows "
            "whether the environment's exposure is rising, stable or falling.",
        ),
        # --------------------------------------------------------- Response --
        "mttr_median": (
            "MTTR (median)",
            "Typical time between identifying a problem and resolving it. It is the middle case: "
            "half of the problems are solved faster than this, half slower. Using the middle case "
            "prevents a few extreme cases from distorting the reading.",
        ),
        "mttr_p90": (
            "MTTR (p90)",
            "The deadline within which 9 out of 10 problems are resolved. While the typical time "
            "shows the day-to-day, this number reveals the cases that take much longer — which is "
            "usually where the relevant risk sits.",
        ),
        "open_never_touched": (
            "Open alerts with no response at all",
            "Percentage of alerts nobody has opened, commented on or handled since they were "
            "created. This is not slowness in resolving: it is the absence of a first response. "
            "This indicator stands in for mean time to first response, which cannot be measured "
            "because the tool records only when the alert is born and when it is closed.",
        ),
        "mttr_by_severity": (
            "Resolution time by severity",
            "Resolution time broken down by severity. The expectation is that the most severe is "
            "resolved fastest; when that does not happen, it signals that the prioritization "
            "defined on paper is not being followed in practice.",
        ),
        # --------------------------------------------------- Vulnerabilities --
        "vulns_critical_high": (
            "Critical and high vulnerabilities",
            "Severe, publicly known security flaws present in the servers' software and still "
            "without a fix applied. Each affected server is counted separately, because each one "
            "needs to be fixed individually.",
        ),
        "vulns_known_exploited": (
            "With known exploit",
            "Flaws for which a ready-made attack tool already exists and is available, or use "
            "confirmed by criminals. The attacker does not need to develop anything — this is the "
            "group to fix first.",
        ),
        "vulns_malware": (
            "Associated with malware/ransomware",
            "Flaws demonstrably already used by viruses and ransomware in real attacks against "
            "other organizations. Not theoretical risk: an attack path with a track record.",
        ),
        "vulns_wormable": (
            "Wormable",
            "Flaws that let an attack spread by itself from one server to another, with no human "
            "action. They are rare, but when they appear they are the top priority, since a single "
            "compromised point can contaminate the whole environment.",
        ),
        "vulns_fixable": (
            "With fix available",
            "Flaws that already have an update published by the vendor. They only depend on "
            "applying the fix — no project, investment or workaround required.",
        ),
        "vulns_hosts_affected": (
            "Affected servers",
            "How many servers have at least one severe flaw pending a fix.",
        ),
        "vulns_by_severity": (
            "Active vulnerabilities by severity",
            "How the flaws found are distributed across severity levels, from critical to "
            "informational, according to the tool's own classification.",
        ),
        "top_vulnerable_hosts": (
            "Servers with the most vulnerabilities",
            "Servers concentrating the largest number of severe flaws. Handling these first "
            "reduces more risk for the same team effort.",
        ),
        # ------------------------------------------------------- Alert mix --
        "alerts_by_category": (
            "Alerts by category",
            "Where the alerts come from: misconfigurations in the cloud environment, behavior "
            "outside the normal pattern observed inside the servers, or correlation of several "
            "signals. The last two are the kind of detection that native cloud provider controls "
            "usually do not deliver.",
        ),
        "top_alert_types": (
            "Most frequent alert types",
            "The alert types that repeat the most. A high, repetitive volume of the same type "
            "usually means a rule that needs tuning, not real risk — it is where the team spends "
            "time with no security gain.",
        ),
        # --------------------------------------------------------- Coverage --
        "coverage_hosts": (
            "Monitored servers",
            "Servers with active monitoring, reporting data continuously.",
        ),
        "coverage_containers": (
            "Containers",
            "Monitored containers. Zero indicates this environment does not use that kind of "
            "technology — it is not a coverage gap.",
        ),
        "coverage_users": (
            "User accounts",
            "User accounts existing on the monitored servers. Represents the environment's access "
            "surface: each account is a door an attacker could use.",
        ),
        "coverage_applications": (
            "Applications",
            "Programs actually running on the servers — not merely installed. Shows what is in "
            "fact active and exposed in the environment.",
        ),
        "coverage_network_interfaces": (
            "Network interfaces",
            "Network connection points identified on the monitored servers.",
        ),
        "coverage_packages": (
            "Software packages",
            "Software components installed on the servers. It is against this inventory that the "
            "search for security flaws is made — without it, there is no way to know what is "
            "vulnerable.",
        ),
        "coverage_cloud_accounts": (
            "Monitored cloud accounts",
            "Cloud accounts connected to monitoring. The same account can have more than one "
            "active connection (for example, one for activity logs and another for configuration "
            "assessment), which is why the number of connections is usually higher.",
        ),
        "cloud_health": (
            "Cloud integration health",
            "The status of each connection to the cloud environment and when each one last "
            "received data. A failing connection means a blind spot: that part of the environment "
            "stops being monitored without anyone noticing.",
        ),
        # ------------------------------------------------------ Operational --
        "open_alerts_table": (
            "Open alerts",
            "The list of alerts not yet handled, with how many days they have been sitting, "
            "ordered by severity. It is the security team's concrete work queue.",
        ),
    },
    "pt": {
        # ----------------------------------------------------------- Alertas --
        "alerts_total": (
            "Alertas (90 dias)",
            "Quantos riscos a ferramenta identificou e sinalizou no período. Reúne três frentes: "
            "erros de configuração no ambiente de nuvem, comportamento fora do padrão observado "
            "dentro dos servidores e ameaças identificadas pela correlação de vários sinais.",
        ),
        "alerts_open_pct": (
            "% em aberto",
            "Quanto do que foi detectado ainda não foi tratado. É o termômetro da capacidade de "
            "resposta: quanto maior, mais risco já identificado segue sem ninguém agir sobre ele.",
        ),
        "alerts_critical_high_open": (
            "Críticos/Altos em aberto",
            "Alertas de maior gravidade que continuam sem tratamento. É a fila que deveria estar "
            "sendo tratada com prioridade e ainda não foi.",
        ),
        "alerts_avg_age": (
            "Idade média (aberto)",
            "Há quanto tempo, em média, os alertas não tratados estão parados. Diferencia um "
            "acúmulo recente e pontual de um problema crônico de processo.",
        ),
        "alerts_last_7d": (
            "Alertas últimos 7d",
            "Volume de novas detecções na última semana, comparado com a semana anterior. Mostra "
            "se a exposição do ambiente está aumentando, estável ou diminuindo.",
        ),
        # -------------------------------------------------------- Resposta --
        "mttr_median": (
            "MTTR (mediana)",
            "Tempo típico entre identificar um problema e resolvê-lo. É o caso do meio: metade "
            "dos problemas é resolvida mais rápido que isso, metade mais devagar. Usar o caso do "
            "meio evita que poucos casos extremos distorçam a leitura.",
        ),
        "mttr_p90": (
            "MTTR (p90)",
            "Prazo dentro do qual 9 de cada 10 problemas são resolvidos. Enquanto o tempo típico "
            "mostra o dia a dia, este número revela os casos que demoram muito mais — que é onde "
            "costuma estar o risco relevante.",
        ),
        "open_never_touched": (
            "Alertas abertos sem qualquer interação",
            "Percentual de alertas que ninguém abriu, comentou ou tratou desde que foram criados. "
            "Não é lentidão na resolução: é ausência de primeiro atendimento. Este indicador ocupa "
            "o lugar do tempo médio até o primeiro atendimento, que não pode ser medido porque a "
            "ferramenta registra apenas quando o alerta nasce e quando é encerrado.",
        ),
        "mttr_by_severity": (
            "Tempo de resolução por gravidade",
            "O tempo de resolução separado por gravidade. O esperado é que o mais grave seja "
            "resolvido mais rápido; quando isso não acontece, é sinal de que a priorização "
            "definida no papel não está sendo seguida na prática.",
        ),
        # --------------------------------------------------- Vulnerabilidades --
        "vulns_critical_high": (
            "Vulnerabilidades críticas e altas",
            "Falhas de segurança graves, já conhecidas publicamente, presentes nos softwares dos "
            "servidores e ainda sem correção aplicada. Cada servidor afetado é contado "
            "separadamente, porque cada um precisa ser corrigido individualmente.",
        ),
        "vulns_known_exploited": (
            "Com exploit conhecido",
            "Falhas para as quais já existe uma ferramenta de ataque pronta e disponível, ou uso "
            "confirmado por criminosos. O atacante não precisa desenvolver nada — é o grupo que "
            "deve ser corrigido primeiro.",
        ),
        "vulns_malware": (
            "Associadas a malware/ransomware",
            "Falhas que comprovadamente já foram usadas por vírus e ransomware em ataques reais "
            "contra outras organizações. Não é risco teórico: é um caminho de ataque com histórico.",
        ),
        "vulns_wormable": (
            "Wormáveis",
            "Falhas que permitem que um ataque se espalhe sozinho de um servidor para outro, sem "
            "qualquer ação humana. São raras, mas quando aparecem têm prioridade máxima, pois um "
            "único ponto comprometido pode contaminar o ambiente inteiro.",
        ),
        "vulns_fixable": (
            "Com correção disponível",
            "Falhas que já têm atualização publicada pelo fabricante. Dependem apenas de aplicar a "
            "correção — não exigem projeto, investimento ou solução alternativa.",
        ),
        "vulns_hosts_affected": (
            "Servidores afetados",
            "Quantos servidores possuem pelo menos uma falha grave pendente de correção.",
        ),
        "vulns_by_severity": (
            "Vulnerabilidades ativas por gravidade",
            "Como as falhas encontradas se distribuem entre os níveis de gravidade, do crítico ao "
            "informativo, conforme a classificação da própria ferramenta.",
        ),
        "top_vulnerable_hosts": (
            "Servidores com mais vulnerabilidades",
            "Servidores que concentram o maior número de falhas graves. Tratar estes primeiro "
            "reduz mais risco com o mesmo esforço da equipe.",
        ),
        # ------------------------------------------------------- Mix de alertas --
        "alerts_by_category": (
            "Alertas por categoria",
            "De onde vêm os alertas: erros de configuração no ambiente de nuvem, comportamento "
            "fora do padrão observado dentro dos servidores, ou correlação de vários sinais. "
            "Os dois últimos são o tipo de detecção que os controles nativos dos provedores de "
            "nuvem normalmente não entregam.",
        ),
        "top_alert_types": (
            "Tipos de alerta mais frequentes",
            "Os tipos de alerta que mais se repetem. Um volume alto e repetitivo do mesmo tipo "
            "costuma indicar regra que precisa de ajuste, e não risco real — é onde a equipe "
            "gasta tempo sem ganho de segurança.",
        ),
        # -------------------------------------------------------- Cobertura --
        "coverage_hosts": (
            "Servidores monitorados",
            "Servidores com monitoramento ativo, enviando dados de forma contínua.",
        ),
        "coverage_containers": (
            "Containers",
            "Containers monitorados. Zero indica que este ambiente não utiliza esse tipo de "
            "tecnologia — não é uma falha de cobertura.",
        ),
        "coverage_users": (
            "Contas de usuário",
            "Contas de usuário existentes nos servidores monitorados. Representa a superfície de "
            "acesso do ambiente: cada conta é uma porta que pode ser usada por um atacante.",
        ),
        "coverage_applications": (
            "Aplicações",
            "Programas efetivamente em execução nos servidores — não apenas instalados. Mostra o "
            "que de fato está ativo e exposto no ambiente.",
        ),
        "coverage_network_interfaces": (
            "Interfaces de rede",
            "Pontos de conexão de rede identificados nos servidores monitorados.",
        ),
        "coverage_packages": (
            "Pacotes de software",
            "Componentes de software instalados nos servidores. É sobre esse inventário que a "
            "busca por falhas de segurança é feita — sem ele, não há como saber o que está "
            "vulnerável.",
        ),
        "coverage_cloud_accounts": (
            "Contas cloud monitoradas",
            "Contas de nuvem conectadas ao monitoramento. Uma mesma conta pode ter mais de uma "
            "conexão ativa (por exemplo, uma para registros de atividade e outra para avaliação "
            "de configuração), por isso o número de conexões costuma ser maior.",
        ),
        "cloud_health": (
            "Saúde das integrações cloud",
            "Situação de cada conexão com o ambiente de nuvem e quando cada uma recebeu dados pela "
            "última vez. Uma conexão com falha significa ponto cego: aquela parte do ambiente "
            "deixa de ser monitorada sem que ninguém perceba.",
        ),
        # ------------------------------------------------------ Operacional --
        "open_alerts_table": (
            "Alertas em aberto",
            "Relação dos alertas ainda não tratados, com há quantos dias estão parados, "
            "ordenados por gravidade. É a fila de trabalho concreta da equipe de segurança.",
        ),
    },
}


# Os tipos de alerta chegam da API com nomes técnicos (NewExternalServerIPConn...).
# Para o relatório executivo eles são traduzidos para o que de fato aconteceu.
ALERT_TYPE_LABELS = {
    "en": {
        "NewExternalServerIPConn": "Server connected to an external address never seen before",
        "NewExternalServerDNSConn": "Server reached an external domain never seen before",
        "NewExternalServerIp": "A new external address started being reached by the environment",
        "NewExternalServerDns": "A new external domain started being reached by the environment",
        "PolicyViolationChanged": "Change in an already known misconfiguration",
        "NewViolations": "New misconfiguration identified",
        "ComplianceChanged": "Change in the result of a compliance check",
        "NewInternalConnection": "New connection between internal servers",
        "NewBinaryType": "Program run for the first time on a server",
        "NewChildLaunched": "Program started another process for the first time",
        "NewExternalClientBadIp": "Connection received from an address with bad reputation",
        "NewExternalServerBadIp": "Server reached an address with bad reputation",
        "NewExternalServerBadDNSConn": "Server reached a domain with bad reputation",
        "NewExternalClientConn": "New external connection received by the environment",
        "NewUser": "New user account created on a server",
        "ChangedFile": "A system file was modified",
        "MaliciousFile": "Malicious file identified on a server",
        "SuspiciousActivityHost": "Suspicious activity detected on a server",
        "NewAzureLoginFromSource": "Azure sign-in from a new source",
        "NewAzureService": "A new Azure service started being used",
        "NewAzureApiCallOnResource": "New administrative operation performed on Azure",
    },
    "pt": {
        "NewExternalServerIPConn": "Servidor conectou-se a um endereço externo nunca visto antes",
        "NewExternalServerDNSConn": "Servidor acessou um domínio externo nunca visto antes",
        "NewExternalServerIp": "Novo endereço externo passou a ser acessado pelo ambiente",
        "NewExternalServerDns": "Novo domínio externo passou a ser acessado pelo ambiente",
        "PolicyViolationChanged": "Mudança em uma falha de configuração já conhecida",
        "NewViolations": "Nova falha de configuração identificada",
        "ComplianceChanged": "Mudança no resultado de uma verificação de conformidade",
        "NewInternalConnection": "Nova conexão entre servidores internos",
        "NewBinaryType": "Programa executado pela primeira vez em um servidor",
        "NewChildLaunched": "Programa iniciou outro processo pela primeira vez",
        "NewExternalClientBadIp": "Conexão recebida de endereço com má reputação",
        "NewExternalServerBadIp": "Servidor acessou endereço com má reputação",
        "NewExternalServerBadDNSConn": "Servidor acessou domínio com má reputação",
        "NewExternalClientConn": "Nova conexão externa recebida pelo ambiente",
        "NewUser": "Nova conta de usuário criada em um servidor",
        "ChangedFile": "Arquivo de sistema foi alterado",
        "MaliciousFile": "Arquivo malicioso identificado em um servidor",
        "SuspiciousActivityHost": "Atividade suspeita detectada em um servidor",
        "NewAzureLoginFromSource": "Acesso ao Azure a partir de uma origem nova",
        "NewAzureService": "Novo serviço do Azure passou a ser utilizado",
        "NewAzureApiCallOnResource": "Nova operação administrativa executada no Azure",
    },
}


def _entry(key):
    lang = get_language()
    return GLOSSARY.get(lang, {}).get(key) or GLOSSARY[DEFAULT_LANG].get(key)


def help_text(key):
    """Texto de tooltip (definição) para o indicador."""
    entrada = _entry(key)
    return entrada[1] if entrada else key


def label(key):
    """Rótulo curto do indicador."""
    entrada = _entry(key)
    return entrada[0] if entrada else key


def entries(keys):
    """Lista de (rótulo, definição) para as chaves pedidas, sem repetir, no idioma
    corrente — usada para montar o glossário impresso."""
    vistos, saida = set(), []
    for key in keys:
        if key in vistos:
            continue
        entrada = _entry(key)
        if entrada:
            vistos.add(key)
            saida.append(entrada)
    return saida


def alert_type_label(alert_type):
    """Descrição em linguagem clara do tipo de alerta; devolve o nome técnico se
    for um tipo ainda não mapeado."""
    lang = get_language()
    mapa = ALERT_TYPE_LABELS.get(lang, ALERT_TYPE_LABELS[DEFAULT_LANG])
    return mapa.get(alert_type) or ALERT_TYPE_LABELS[DEFAULT_LANG].get(alert_type, alert_type)


def all_keys():
    return list(GLOSSARY[DEFAULT_LANG])
