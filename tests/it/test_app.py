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
from unittest.mock import patch

import pytest
from _pytest.legacypath import TempdirFactory
from click.testing import CliRunner

from ondivi.entry import main


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
@pytest.mark.parametrize('version', [
    ('gitpython==2.1.15',),
    ('gitpython', '-U'),
])
def test_gitpython_versions(version: tuple[str]) -> None:
    """Test script with different gitpython versions."""
    subprocess.run(['venv/bin/pip', 'install', *version], check=True)
    with subprocess.Popen(['venv/bin/flake8', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
@pytest.mark.parametrize('version', [
    ('parse==1.4',),
    ('parse', '-U'),
])
def test_parse_versions(version: tuple[str]) -> None:
    """Test script with different parse versions."""
    subprocess.run(['venv/bin/pip', 'install', *version], check=True)
    with subprocess.Popen(['venv/bin/flake8', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
@pytest.mark.parametrize('version', [
    ('click==0.1',),
    ('click', '-U'),
])
def test_click_versions(version: tuple[str]) -> None:
    """Test script with different click versions."""
    subprocess.run(['venv/bin/pip', 'install', *version], check=True)
    with subprocess.Popen(['venv/bin/flake8', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test() -> None:
    """Test script with real git repo."""
    with subprocess.Popen(['venv/bin/flake8', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi', '--baseline', '56faa56'],
            stdin=lint_proc.stdout,
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
    with subprocess.Popen(['venv/bin/flake8', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_ruff() -> None:
    """Test ruff."""
    with subprocess.Popen(['venv/bin/ruff', 'check', '--select=ALL', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
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
    with subprocess.Popen(['venv/bin/mypy', 'file.py'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
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
    with subprocess.Popen(['echo', ''], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.returncode == 0


@pytest.mark.usefixtures('_test_repo')
def test_info_message() -> None:
    """Test exit with info message."""
    with subprocess.Popen(['echo', 'All files corect!'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.stdout.decode('utf-8').strip() == 'All files corect!'
    assert got.returncode == 0


@pytest.mark.usefixtures('_test_repo')
def test_format() -> None:
    """Test with custom format."""
    with subprocess.Popen(['echo', 'line=12 file=file.py message=`print` found'], stdout=subprocess.PIPE) as lint_proc:
        got = subprocess.run(
            ['venv/bin/ondivi', '--format', 'line={line_num:d} file={filename} {other}'],
            stdin=lint_proc.stdout,
            stdout=subprocess.PIPE,
            check=False,
        )

    assert got.stdout.decode('utf-8').strip() == 'line=12 file=file.py message=`print` found'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_click_app() -> None:
    """Test click app."""
    got = CliRunner().invoke(main, input='\n'.join([
        'file.py:3:1: E302 expected 2 blank lines, found 1',
        'file.py:9:1: E302 expected 2 blank lines, found 1',
        'file.py:10:80: E501 line too long (123 > 79 characters)',
        'file.py:12:80: E501 line too long (119 > 79 characters)',
        'file.py:14:1: E305 expected 2 blank lines after class or function definition, found 1',
    ]))

    assert got.exit_code == 1
    assert got.stdout.strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'


@pytest.fixture()
def _broke_cli() -> Generator[None, None, None]:
    with patch('ondivi.entry.cli') as cli_patch:
        cli_patch.side_effect = ValueError('Fail')
        yield


@pytest.mark.usefixtures('_broke_cli')
def test_handle_exception() -> None:
    """Test handle exception."""
    got = CliRunner().invoke(main, input='')

    assert got.exit_code == 1
    assert len(got.stdout.strip().splitlines()) > 10
    assert got.stdout.strip().splitlines()[:5] == [
        'Ondivi fail with: "Fail"',
        'Please submit it to https://github.com/blablatdinov/ondivi/issues',
        'Copy and paste this stack trace to GitHub:',
        '========================================',
        'Traceback (most recent call last):',
    ]
    assert got.stdout.strip().splitlines()[-1] == 'ValueError: Fail'
