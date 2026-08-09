# --- Stage 1: builder -------------------------------------------------------
# Builds an isolated virtualenv containing the installed package and its
# dependencies. Kept separate from the runtime stage so build-only tooling
# (pip's own cache, wheel builds, etc.) never ends up in the shipped image.
FROM python:3.12-slim-bookworm AS builder

# Skip pip's self-update nag and disable its download cache; neither is useful
# in a throwaway build layer and the cache would just bloat this stage.
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Create a venv rather than installing into the system Python so the runtime
# stage can copy /opt/venv wholesale without dragging in build-time state.
RUN python -m venv /opt/venv
# Copy only what `pip install .` needs (metadata + source) before installing,
# so Docker's layer cache is invalidated by source changes, not unrelated files.
COPY pyproject.toml README.md ./
COPY src ./src
RUN /opt/venv/bin/python -m pip install --upgrade pip && \
    /opt/venv/bin/python -m pip install .


# --- Stage 2: runtime --------------------------------------------------------
# Minimal image that only contains the installed venv plus the config/fixture
# files the app needs at runtime. No compilers, no source tree, no pip cache.
FROM python:3.12-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Matplotlib wants a writable config dir; point it at the tmpfs mount
    # since the rest of the filesystem is read-only at runtime (see compose.yaml).
    MPLCONFIGDIR=/tmp/matplotlib \
    SCOLIOSIS_PROJECT_ROOT=/app \
    SCOLIOSIS_API_OUTPUT_DIR=/app/data/outputs/api

# libglib2.0-0/libgomp1 are shared-library dependencies of opencv-python-headless.
# Install them, then drop apt's package lists in the same layer to keep the
# image small. Also provision a fixed-uid, non-root, login-less service account
# up front so nothing later in the build needs to run as root.
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

# Pull in only the built venv (no source, no build tools) plus the runtime
# assets the app reads directly off disk: pipeline config and the bundled
# synthetic fixtures used by the /demo/synthetic endpoint.
COPY --from=builder /opt/venv /opt/venv
COPY config ./config
COPY tests/fixtures ./tests/fixtures

# Pre-create the directories the app writes to and hand them to appuser,
# since the container filesystem is otherwise mounted read-only (compose.yaml).
RUN mkdir -p /app/data/outputs/api /tmp/matplotlib && \
    chown -R appuser:appuser /app/data/outputs /tmp/matplotlib

# Drop root for the rest of the image's life; combined with cap_drop/no-new-
# privileges in compose.yaml this limits blast radius if the app is compromised.
USER appuser

EXPOSE 8000

# Polls the app's own /health route so `docker ps`/orchestrators can detect a
# hung or crashed server, not just a dead process.
HEALTHCHECK --interval=30s --timeout=3s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

# Ensure `docker stop` sends SIGTERM (uvicorn's graceful-shutdown signal)
# rather than a default that some base images override.
STOPSIGNAL SIGTERM

# --no-server-header avoids advertising the web server implementation/version
# in responses.
CMD ["uvicorn", "scoliosis_platform.api:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
