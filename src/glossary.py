"""Definições dos indicadores — fonte única de verdade.

Usado como tooltip (`help=`) nos dashboards, como `title=` nos cards do relatório
e para montar o glossário impresso. Manter as definições aqui evita que dashboard
e relatório expliquem o mesmo número de formas diferentes.

Linguagem: o público é o decisor (CISO/diretoria), não o analista. Cada definição
diz o que o número significa e por que importa — sem nomes de campo, sem jargão
de API e sem fórmula. A precisão é mantida: quando a contagem tem uma regra que
muda a leitura (ex.: o mesmo problema contado uma vez por servidor), isso é dito
em português claro.

Cada entrada: (rótulo curto, definição).
"""

GLOSSARY = {
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
    # -------------------------------------------------- Tempo de resposta --
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
        "informativo, segundo a classificação da própria ferramenta.",
    ),
    "top_vulnerable_hosts": (
        "Servidores com mais vulnerabilidades",
        "Servidores que concentram o maior número de falhas graves. Tratar estes primeiro "
        "reduz mais risco com o mesmo esforço da equipe.",
    ),
    # ------------------------------------------------------- Alertas: mix --
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
    # ----------------------------------------------------------- Cobertura --
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
    # -------------------------------------------------------- Operacional --
    "open_alerts_table": (
        "Alertas em aberto",
        "Relação dos alertas ainda não tratados, com há quantos dias estão parados, "
        "ordenados por gravidade. É a fila de trabalho concreta da equipe de segurança.",
    ),
}


# Os tipos de alerta chegam da API com nomes técnicos (NewExternalServerIPConn...).
# Para o relatório executivo eles são traduzidos para o que de fato aconteceu.
ALERT_TYPE_LABELS = {
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
}


def alert_type_label(alert_type):
    """Descrição em linguagem clara do tipo de alerta; devolve o nome técnico se
    for um tipo ainda não mapeado."""
    return ALERT_TYPE_LABELS.get(alert_type, alert_type)


def help_text(key):
    """Texto de tooltip (definição) para o indicador."""
    return GLOSSARY[key][1]


def label(key):
    """Rótulo curto do indicador."""
    return GLOSSARY[key][0]
