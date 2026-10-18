FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir -r requirements.txt -c requirements.lock && useradd --uid 10001 --create-home moviegame
COPY --chown=moviegame:moviegame app ./app
COPY --chown=moviegame:moviegame data ./data
COPY --chown=moviegame:moviegame web ./web
USER moviegame
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--limit-concurrency", "128", "--timeout-keep-alive", "5", "--timeout-graceful-shutdown", "30", "--no-access-log"]
