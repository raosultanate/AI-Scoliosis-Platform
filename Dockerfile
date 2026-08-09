FROM python:3.12-slim-bookworm AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN python -m venv /opt/venv
COPY pyproject.toml README.md ./
COPY src ./src
RUN /opt/venv/bin/python -m pip install --upgrade pip && \
    /opt/venv/bin/python -m pip install .


FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    SCOLIOSIS_PROJECT_ROOT=/app \
    SCOLIOSIS_API_OUTPUT_DIR=/app/data/outputs/api

RUN apt-get update && \
    apt-get install --yes --no-install-recommends libglib2.0-0 libgomp1 && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 10001 appuser && \
    useradd \
        --uid 10001 \
        --gid appuser \
        --create-home \
        --shell /usr/sbin/nologin \
        appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY config ./config
COPY tests/fixtures ./tests/fixtures

RUN mkdir -p /app/data/outputs/api /tmp/matplotlib && \
    chown -R appuser:appuser /app/data/outputs /tmp/matplotlib

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

STOPSIGNAL SIGTERM

CMD ["uvicorn", "scoliosis_platform.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
