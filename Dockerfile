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
ENV PATH="/root/.local/bin:$PATH"
WORKDIR /app
RUN cd /app
RUN pip install poetry==2.1.3
RUN apt-get update && apt-get install curl git -y
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /bin
RUN curl -O -L -C - https://github.com/editorconfig-checker/editorconfig-checker/releases/download/$EC_VERSION/ec-linux-amd64.tar.gz && \
    tar xzf ec-linux-amd64.tar.gz -C /tmp && \
    mkdir -p /root/.local/bin && \
    mv /tmp/bin/ec-linux-amd64 /root/.local/bin/ec
COPY poetry.lock pyproject.toml /app/
COPY lint-requirements.txt /app/
RUN python3 -m venv lint-venv
RUN ./lint-venv/bin/pip install -r lint-requirements.txt
RUN poetry install
COPY . .
