# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

FROM python:3.14.3
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV EC_VERSION="v3.0.3"
ENV POETRY_NO_INTERACTION=1
ENV PATH="/root/.local/bin:$PATH"

RUN pip install poetry==2.1.3
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /bin

ENV EC_VERSION="v3.0.3"
RUN curl -O -L -C - https://github.com/editorconfig-checker/editorconfig-checker/releases/download/$EC_VERSION/ec-linux-amd64.tar.gz && \
    tar xzf ec-linux-amd64.tar.gz -C /tmp && \
    mkdir -p /root/.local/bin && \
    mv /tmp/bin/ec-linux-amd64 /root/.local/bin/ec && \
    rm ec-linux-amd64.tar.gz

WORKDIR /app

COPY poetry.lock pyproject.toml README.md ./

COPY . .
RUN poetry install

RUN ln -sf /app/.venv/bin/python /usr/local/bin/poetry-python && \
    ln -sf /app/.venv/bin/pip /usr/local/bin/poetry-pip && \
    ln -sf /app/lint-venv/bin/python /usr/local/bin/lint-python && \
    ln -sf /app/lint-venv/bin/pip /usr/local/bin/lint-pip

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV LINT_VENV=/app/lint-venv
ENV LINT_PATH="/app/lint-venv/bin:$PATH"

RUN echo '#!/bin/bash\n\
export VIRTUAL_ENV=/app/.venv\n\
export PATH="/app/.venv/bin:$PATH"\n\
export LINT_VENV=/app/lint-venv\n\
export LINT_PATH="/app/lint-venv/bin:$PATH"\n\
exec "$@"' > /usr/local/bin/activate-env && \
    chmod +x /usr/local/bin/activate-env

RUN useradd --create-home --shell /bin/bash developer && \
    chown -R developer:developer /app

USER developer
WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
