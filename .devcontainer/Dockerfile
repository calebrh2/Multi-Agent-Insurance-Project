FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN python -m pip install --no-cache-dir \
    ruff \
    mypy \
    pydantic \
    pytest \
    uv
