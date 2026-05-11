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

COPY ./compose/local/fastapi/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./compose/local/fastapi/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

COPY ./compose/local/fastapi/celery/worker/start /celery/worker/start
RUN sed -i 's/\r$//g' /celery/worker/start && chmod +x /celery/worker/start

COPY ./compose/local/fastapi/celery/beat/start /celery/beat/start
RUN sed -i 's/\r$//g' /celery/beat/start && chmod +x /celery/beat/start

COPY ./compose/local/fastapi/celery/flower/start /celery/flower/start
RUN sed -i 's/\r$//g' /celery/flower/start && chmod +x /celery/flower/start

ENTRYPOINT ["/entrypoint"]
CMD ["/start"]
