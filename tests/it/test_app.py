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
import uuid
import zipfile
from collections.abc import Generator
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest
import tomli
from _pytest.legacypath import TempdirFactory
from click.testing import CliRunner
from typing_extensions import TypeAlias

from ondivi.entry import main

_RUN_SHELL_T: TypeAlias = Callable[[list[str], list[str]], subprocess.CompletedProcess[bytes]]


@pytest.fixture(scope='module')
def current_dir() -> Path:
    """Current directory for installing actual ondivi."""
    return Path().absolute()


def _version_from_lock(package_name: str) -> str:
    return '{0}=={1}'.format(
        package_name,
        next(
            package
            for package in tomli.loads(Path('poetry.lock').read_text(encoding='utf-8'))['package']
            if package['name'] == package_name
        )['version'],
    )


# flake8: noqa: S603, S607. Not a production code
@pytest.fixture(scope='module')
def _test_repo(tmpdir_factory: TempdirFactory, current_dir: str) -> Generator[Path, None, None]:
    """Real git repository."""
    tmp_path = tmpdir_factory.mktemp('test')
    with zipfile.ZipFile('tests/fixtures/ondivi-test-repo.zip', 'r') as zip_ref:
        zip_ref.extractall(tmp_path)
    os.chdir(tmp_path / 'ondivi-test-repo')
    subprocess.run(['python', '-m', 'venv', 'venv'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'pip', '-U'], check=True)
    subprocess.run(['venv/bin/pip', 'install', 'flake8', 'ruff', 'mypy', str(current_dir)], check=True)
    yield tmp_path
    os.chdir(current_dir)


@pytest.fixture
def run_shell() -> _RUN_SHELL_T:
    """Run commands with pipe in shell."""
    def _exec(lint_cmd: list[str], ondivi_cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
        with subprocess.Popen(lint_cmd, stdout=subprocess.PIPE) as lint_proc:
            return subprocess.run(
                ondivi_cmd,
                stdin=lint_proc.stdout,
                stdout=subprocess.PIPE,
                check=False,
            )
    return _exec


@pytest.fixture
def file_with_violations(_test_repo: Path) -> Path:
    """File contain violations from linter."""
    violations_file = _test_repo / 'violations.txt'
    violations_file.write_text(
        '\n'.join([
            'file.py:3:1: E302 expected 2 blank lines, found 1',
            'file.py:9:1: E302 expected 2 blank lines, found 1',
            'file.py:10:80: E501 line too long (123 > 79 characters)',
            'file.py:12:80: E501 line too long (119 > 79 characters)',
            'file.py:14:1: E305 expected 2 blank lines after class or function definition, found 1',
        ]),
        encoding='utf-8',
    )
    return violations_file


@pytest.mark.usefixtures('_test_repo')
@pytest.mark.parametrize('version', [
    ('gitpython==2.1.15',),
    (_version_from_lock('gitpython'),),
    ('gitpython', '-U'),
    ('parse==1.4',),
    (_version_from_lock('parse'),),
    ('parse', '-U'),
    ('click==0.1',),
    (_version_from_lock('click'),),
    ('click', '-U'),
])
def test_dependency_versions(version: tuple[str], run_shell: _RUN_SHELL_T) -> None:
    """Test script with different dependency versions."""
    subprocess.run(['venv/bin/pip', 'install', *version], check=True)
    got = run_shell(['venv/bin/flake8', 'file.py'], ['venv/bin/ondivi'])

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test(run_shell: _RUN_SHELL_T) -> None:
    """Test script with real git repo."""
    got = run_shell(['venv/bin/flake8', 'file.py'], ['venv/bin/ondivi', '--baseline', '56faa56'])

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        'file.py:3:1: E302 expected 2 blank lines, found 1',
        'file.py:9:1: E302 expected 2 blank lines, found 1',
        'file.py:12:80: E501 line too long (119 > 79 characters)',
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_baseline_default(run_shell: _RUN_SHELL_T) -> None:
    """Test baseline default."""
    got = run_shell(['venv/bin/flake8', 'file.py'], ['venv/bin/ondivi'])

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_ruff(run_shell: _RUN_SHELL_T) -> None:
    """Test ruff."""
    got = run_shell(
        ['venv/bin/ruff', 'check', '--select=ALL', 'file.py', '--output-format=concise'],
        ['venv/bin/ondivi'],
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
def test_mypy(run_shell: _RUN_SHELL_T) -> None:
    """Test mypy."""
    got = run_shell(['venv/bin/mypy', 'file.py'], ['venv/bin/ondivi'])

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        'file.py:16: error: Argument 2 to "User" has incompatible type "str"; expected "int"  [arg-type]',
        'Found 2 errors in 1 file (checked 1 source file)',
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_without_violations(run_shell: _RUN_SHELL_T) -> None:
    """Test exit without violations."""
    got = run_shell(['echo', ''], ['venv/bin/ondivi'])

    assert got.returncode == 0


@pytest.mark.usefixtures('_test_repo')
def test_info_message(run_shell: _RUN_SHELL_T) -> None:
    """Test exit with info message."""
    got = run_shell(['echo', 'All files correct!'], ['venv/bin/ondivi'])

    assert got.stdout.decode('utf-8').strip() == 'All files correct!'
    assert got.returncode == 0


@pytest.mark.usefixtures('_test_repo')
def test_format(run_shell: _RUN_SHELL_T) -> None:
    """Test with custom format."""
    got = run_shell(
        ['echo', 'line=12 file=file.py message=`print` found'],
        ['venv/bin/ondivi', '--format', 'line={line_num:d} file={filename} {other}'],
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


@pytest.fixture
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


@pytest.mark.usefixtures('_test_repo')
def test_only_violations(run_shell: _RUN_SHELL_T) -> None:
    """Test only violations."""
    got = run_shell(
        ['venv/bin/ruff', 'check', '--select=ALL', 'file.py', '--output-format=concise'],
        ['venv/bin/ondivi', '--only-violations'],
    )

    assert got.stdout.decode('utf-8').strip() == '\n'.join([
        'file.py:12:5: T201 `print` found',
        'file.py:12:11: Q000 [*] Single quotes found but double quotes preferred',
        'file.py:12:89: E501 Line too long (119 > 88)',
        'file.py:16:16: Q000 [*] Single quotes found but double quotes preferred',
        'file.py:16:23: Q000 [*] Single quotes found but double quotes preferred',
    ])
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_fromfile(file_with_violations: Path) -> None:
    """Test script with violations from file."""
    got = subprocess.run(
        ['venv/bin/ondivi', '--fromfile', str(file_with_violations)],
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == 'file.py:12:80: E501 line too long (119 > 79 characters)'
    assert got.returncode == 1


@pytest.mark.usefixtures('_test_repo')
def test_fromfile_not_found() -> None:
    """Test script with violations from file."""
    got = subprocess.run(
        ['venv/bin/ondivi', '--fromfile', 'undefined.txt'],
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == 'File with violations "undefined.txt" not found'
    assert got.returncode == 1
