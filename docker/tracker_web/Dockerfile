FROM python:3.11-slim as builder

WORKDIR /tracker

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /tracker

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app app

RUN mkdir -p /tracker/logs && chown -R app:app /tracker/logs
RUN touch /tracker/logs/django_errors.log && chown app:app /tracker/logs/django_errors.log

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/tracker_web/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --chown=app:app . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/tracker

RUN python manage.py collectstatic --noinput

USER app

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "taskboard.wsgi:application"]
