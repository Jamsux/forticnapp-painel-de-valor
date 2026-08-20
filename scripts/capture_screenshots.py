#!/usr/bin/env python3
"""Captura as telas do painel em modo demonstração (dados anonimizados).

O Streamlit é uma aplicação JavaScript: o `--screenshot` do Chrome headless
dispara antes da renderização e produz uma página em branco. Por isso aqui o
navegador é controlado pelo protocolo de depuração (CDP), que permite esperar a
página ficar pronta antes de capturar.

Uso (com o app demo rodando em :8502):
    FORTICNAPP_DEMO=1 APP_LANG=en .venv/bin/streamlit run dashboard/Home.py --server.port 8502
    python3 scripts/capture_screenshots.py
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src import browser  # noqa: E402

BASE_URL = os.environ.get("DEMO_URL", "http://localhost:8502")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots")
DEBUG_PORT = 9333


# URLs vêm do nome do arquivo em dashboard/views/, não do título traduzido —
# então não mudam com o idioma.
PAGES = [
    ("executive-view", "/executive", 1440, 2400),
    ("security-operations", "/operations", 1440, 2600),
    ("report", "/report", 1440, 2000),
]


async def capture(ws_url, url, width, height, destino):
    async with websockets.connect(ws_url, max_size=100 * 1024 * 1024) as ws:
        seq = iter(range(1, 10_000))

        async def cmd(method, params=None):
            msg_id = next(seq)
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                resp = json.loads(await ws.recv())
                if resp.get("id") == msg_id:
                    return resp.get("result", {})

        await cmd("Emulation.setDeviceMetricsOverride",
                  {"width": width, "height": height, "deviceScaleFactor": 2, "mobile": False})
        # o headless assume tema escuro por padrão; a documentação usa o tema claro
        await cmd("Emulation.setEmulatedMedia",
                  {"features": [{"name": "prefers-color-scheme", "value": "light"}]})
        await cmd("Page.enable")
        await cmd("Page.navigate", {"url": url})
        await asyncio.sleep(10)  # espera o Streamlit montar a página e desenhar os gráficos
        # a viewport já é alta o bastante para conter a página inteira; basta
        # garantir que nada ficou rolado (janela e contêiner interno do Streamlit)
        await cmd("Runtime.evaluate", {"expression":
                  "window.scrollTo(0,0);"
                  "document.querySelectorAll('section,div').forEach(e=>{"
                  "  if(e.scrollTop) e.scrollTop = 0;"
                  "});"})
        await asyncio.sleep(3)

        # sem captureBeyondViewport: a viewport já é alta o bastante e, com os
        # contêineres de rolagem do Streamlit, essa opção desalinha a captura
        res = await cmd("Page.captureScreenshot", {"format": "png"})
        with open(destino, "wb") as fh:
            fh.write(base64.b64decode(res["data"]))
        return os.path.getsize(destino)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    chrome = browser.find_chrome()
    if not chrome:
        print(f"[erro] {browser.MENSAGEM_AUSENTE}")
        sys.exit(1)
    perfil = tempfile.mkdtemp(prefix="chrome-shots-")
    proc = subprocess.Popen(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
         f"--remote-debugging-port={DEBUG_PORT}", f"--user-data-dir={perfil}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):  # aguarda a porta de depuração responder
            try:
                urllib.request.urlopen(f"http://localhost:{DEBUG_PORT}/json/version", timeout=1)
                break
            except Exception:
                time.sleep(0.5)
        else:
            print("[erro] Chrome não respondeu na porta de depuração.")
            sys.exit(1)

        for nome, caminho, w, h in PAGES:
            alvo = urllib.request.quote(BASE_URL + caminho, safe=":/")
            # /json/new exige PUT nas versões recentes do Chrome
            req = urllib.request.Request(
                f"http://localhost:{DEBUG_PORT}/json/new?about:blank", method="PUT")
            with urllib.request.urlopen(req) as r:
                alvo_info = json.load(r)
            destino = os.path.abspath(os.path.join(OUT_DIR, f"{nome}.png"))
            tamanho = asyncio.run(capture(alvo_info["webSocketDebuggerUrl"], alvo, w, h, destino))
            print(f"  {nome}.png ({tamanho // 1024} KB)")
            urllib.request.urlopen(
                f"http://localhost:{DEBUG_PORT}/json/close/{alvo_info['id']}").read()
    finally:
        proc.terminate()
    print(f"Capturas salvas em {os.path.normpath(OUT_DIR)}")


if __name__ == "__main__":
    main()
