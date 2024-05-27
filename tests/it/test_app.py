# The MIT License (MIT).
#
# Copyright (c) 2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Integration test with installing and check on real git repo."""

import os
import subprocess
import zipfile
from pathlib import Path

import pytest
from _pytest.legacypath import TempdirFactory


@pytest.fixture(scope='module')
def current_dir() -> Path:
    """Current directory for installing actual ondivi."""
    return Path().absolute()


# flake8: noqa: S603, S607. Not a production code
@pytest.fixture(scope='module')
def _test_repo(tmpdir_factory: TempdirFactory, current_dir: str) -> None:
    """Real git repository."""
    tmp_path = tmpdir_factory.mktemp('test')
    with zipfile.ZipFile('tests/fixtures/ondivi-test-repo.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    os.chdir(tmp_path / 'ondivi-test-repo')
    subprocess.run(['python', '-m', 'venv', 'venv'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'pip', '-U'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'flake8', 'ruff', str(current_dir)], check=True)


@pytest.mark.usefixtures('_test_repo')
@pytest.mark.parametrize('version', ['>=2,<3', '>=3'])
def test_gitpython_versions(version) -> None:
    """Test script with different gitpython versions."""
    subprocess.run(['venv/bin/pip', 'install', 'gitpython{0}'.format(version)], check=True)
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['venv/bin/flake8', 'file.py'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    ).stdout.decode('utf-8').strip()

    assert got == 'file.py:4:80: E501 line too long (119 > 79 characters)'


@pytest.mark.usefixtures('_test_repo')
def test() -> None:
    """Test script with real git repo."""
    got = subprocess.run(
        ['venv/bin/ondivi', '--baseline', '56faa56'],
        stdin=subprocess.Popen(
            ['venv/bin/flake8', 'file.py'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    ).stdout.decode('utf-8').strip()

    assert got == 'file.py:4:80: E501 line too long (119 > 79 characters)'


@pytest.mark.usefixtures('_test_repo')
def test_baseline_default() -> None:
    """Test baseline default."""
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['venv/bin/flake8', 'file.py'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    ).stdout.decode('utf-8').strip()

    assert got == 'file.py:4:80: E501 line too long (119 > 79 characters)'


@pytest.mark.usefixtures('_test_repo')
def test_ruff() -> None:
    """Test ruff."""
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['venv/bin/ruff', 'check', '--select=ALL', 'file.py'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    ).stdout.decode('utf-8').strip()

    assert got == '\n'.join([
        'file.py:4:5: T201 `print` found',
        'file.py:4:11: Q000 [*] Single quotes found but double quotes preferred',
        'file.py:4:89: E501 Line too long (119 > 88)',
        'Found 13 errors.',
        '[*] 4 fixable with the `--fix` option (4 hidden fixes can be enabled with the `--unsafe-fixes` option).',
    ])
