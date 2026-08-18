FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# config/ e data/ são preenchidos em runtime (montados como volume) — não fazem parte da imagem
RUN mkdir -p /app/config /app/data

ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PYTHONUNBUFFERED=1

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

CMD ["streamlit", "run", "dashboard/Home.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
