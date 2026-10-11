FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Workspace is a virtiofs mount, so Git's ownership check fails intermittently.
RUN git config --system --add safe.directory '*'

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN python -m pip install --no-cache-dir \
    ruff \
    mypy \
    pydantic \
    pytest \
    uv
