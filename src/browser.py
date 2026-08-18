"""Localiza o Chrome/Chromium instalado, em qualquer sistema operacional.

Usado para gerar o PDF do relatório e as capturas de tela. Fica em um módulo
próprio para que os dois scripts usem exatamente a mesma lógica de descoberta.
"""
import os
import shutil

# Nomes no PATH: cobre instalações via gerenciador de pacotes e o `chrome` do Windows
NOMES_NO_PATH = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "chrome", "msedge",
]

CAMINHOS_CONHECIDOS = [
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    # Linux
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    # Windows
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome():
    """Devolve o caminho do navegador ou None. A variável de ambiente
    CHROME_PATH tem prioridade, para instalações fora do lugar padrão."""
    definido = os.environ.get("CHROME_PATH")
    if definido and os.path.exists(definido):
        return definido

    for nome in NOMES_NO_PATH:
        encontrado = shutil.which(nome)
        if encontrado:
            return encontrado

    for caminho in CAMINHOS_CONHECIDOS:
        # no Windows o perfil do usuário também é um local comum de instalação
        expandido = os.path.expandvars(os.path.expanduser(caminho))
        if os.path.exists(expandido):
            return expandido

    local_app = os.environ.get("LOCALAPPDATA")
    if local_app:
        candidato = os.path.join(local_app, "Google", "Chrome", "Application", "chrome.exe")
        if os.path.exists(candidato):
            return candidato
    return None


MENSAGEM_AUSENTE = (
    "Chrome/Chromium não encontrado. Instale o Google Chrome, ou defina a variável "
    "de ambiente CHROME_PATH apontando para o executável. Alternativa: gere o "
    "relatório em HTML (sem --pdf) e use Ctrl+P no navegador."
)
