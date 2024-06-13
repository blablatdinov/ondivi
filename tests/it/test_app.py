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
from collections.abc import Generator
from pathlib import Path

import pytest
from _pytest.legacypath import TempdirFactory


@pytest.fixture(scope='module')
def current_dir() -> Path:
    """Current directory for installing actual ondivi."""
    return Path().absolute()


# flake8: noqa: S603, S607. Not a production code
@pytest.fixture(scope='module')
def _test_repo(tmpdir_factory: TempdirFactory, current_dir: str) -> Generator[None, None, None]:
    """Real git repository."""
    tmp_path = tmpdir_factory.mktemp('test')
    with zipfile.ZipFile('tests/fixtures/ondivi-test-repo.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    os.chdir(tmp_path / 'ondivi-test-repo')
    subprocess.run(['python', '-m', 'venv', 'venv'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'pip', '-U'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'flake8', 'ruff', 'mypy', str(current_dir)], check=True)
    yield
    os.chdir(current_dir)


@pytest.mark.usefixtures('_test_repo')
@pytest.mark.parametrize('version', ['>=2,<3', '>=3'])
def test_gitpython_versions(version: str) -> None:
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
    )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
@pytest.mark.parametrize('version', [
    ('parse==1.3.2',),
    ('parse', '-U'),
])
def test_parse_versions(version: str) -> None:
    """Test script with different parse versions."""
    subprocess.run(['venv/bin/pip', 'install', *version], check=True)
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['venv/bin/flake8', 'file.py'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


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
    )

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        'file.py:3:1: E302 expected 2 blank lines, found 1',
        'file.py:9:1: E302 expected 2 blank lines, found 1',
        'file.py:12:80: E501 line too long (119 > 79 characters)',
    ]
    assert got.returncode == 1


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
    )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


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
    )

    assert got.stdout.decode('utf-8').strip() == '\n'.join([
        'file.py:12:5: T201 `print` found',
        'file.py:12:11: Q000 [*] Single quotes found but double quotes preferred',
        'file.py:12:89: E501 Line too long (119 > 88)',
        'file.py:16:16: Q000 [*] Single quotes found but double quotes preferred',
        'file.py:16:23: Q000 [*] Single quotes found but double quotes preferred',
        'Found 17 errors.',
        '[*] 8 fixable with the `--fix` option (4 hidden fixes can be enabled with the `--unsafe-fixes` option).',
    ])
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_mypy() -> None:
    """Test mypy."""
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['venv/bin/mypy', 'file.py'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        'file.py:16: error: Argument 2 to "User" has incompatible type "str"; expected "int"  [arg-type]',
        'Found 2 errors in 1 file (checked 1 source file)',
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_without_violations() -> None:
    """Test exit without violations."""
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['echo', ''],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.returncode == 0


@pytest.mark.usefixtures('_test_repo')
def test_info_message() -> None:
    """Test exit with info message."""
    got = subprocess.run(
        ['venv/bin/ondivi'],
        stdin=subprocess.Popen(
            ['echo', 'All files corect!'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == 'All files corect!'
    assert got.returncode == 0


@pytest.mark.usefixtures('_test_repo')
def test_format() -> None:
    """Test with custom format."""
    got = subprocess.run(
        ['venv/bin/ondivi', '--format', 'line={line_num:d} file={filename}{other}'],
        stdin=subprocess.Popen(
            ['echo', 'line=12 filename=file.py message=`print` found'],
            stdout=subprocess.PIPE,
        ).stdout,
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == 'line=12 filename=file.py message=`print` found'
    assert got.returncode == 0
