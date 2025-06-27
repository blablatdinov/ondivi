# The MIT License (MIT).
#
# Copyright (c) 2024-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

FROM python:3.13.5
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
COPY lint-requirements.txt ./

COPY . .
RUN poetry install

RUN python3 -m venv /app/lint-venv
RUN /app/lint-venv/bin/pip install -r lint-requirements.txt

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
