FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN cp /app/compose/local/fastapi/entrypoint /entrypoint \
    && cp /app/compose/local/fastapi/start /start \
    && mkdir -p /celery/worker /celery/beat /celery/flower \
    && cp /app/compose/local/fastapi/celery/worker/start /celery/worker/start \
    && cp /app/compose/local/fastapi/celery/beat/start /celery/beat/start \
    && cp /app/compose/local/fastapi/celery/flower/start /celery/flower/start \
    && sed -i 's/\r$//g' /entrypoint /start /celery/worker/start /celery/beat/start /celery/flower/start \
    && chmod +x /entrypoint /start /celery/worker/start /celery/beat/start /celery/flower/start

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
