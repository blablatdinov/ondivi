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

"""Integration test with installing and check on real git repo."""

import os
import sys
import subprocess
from collections.abc import Generator
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import pytest
import tomli
from _pytest.legacypath import TempdirFactory
from click.testing import CliRunner
from git import Repo
from typing_extensions import TypeAlias

from ondivi.entry import main
from tests.helpers.define_repo import define_repo

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


@pytest.fixture
def bin_dir() -> Path:
    """Directory with binaries for run."""
    if os.name == 'nt':
        return Path('venv/Scripts')
    else:
        return Path('venv/bin')


# flake8: noqa: S603, S607. Not a production code
@pytest.fixture(scope='module')
def test_repo(tmpdir_factory: TempdirFactory, current_dir: str) -> Generator[Path, None, None]:
    """Real git repository."""
    tmp_path = tmpdir_factory.mktemp('test')
    repo_path = tmp_path / 'ondivi-test-repo'
    repo_path.mkdir()
    define_repo(Path('tests/fixtures/test-repo.yaml').read_text(), repo_path)
    os.chdir(repo_path)
    subprocess.run(['python', '-m', 'venv', 'venv'], check=True)
    is_windows = os.name == 'nt'
    pip_path = Path('venv/Scripts/pip') if is_windows else Path('venv/bin/pip')
    if is_windows:
        subprocess.run([str(Path('venv/Scripts/python')), '-m', 'pip', 'install', 'pip', '-U'], check=True)
    else:
        subprocess.run([str(pip_path), 'install', 'pip', '-U'], check=True)
    subprocess.run([str(pip_path), 'install', 'flake8', 'ruff', 'mypy', str(current_dir)], check=True)
    yield tmp_path
    os.chdir(current_dir)


@pytest.fixture
def revisions(test_repo: Path) -> tuple[str, ...]:
    """List of commit hashes."""
    return tuple(str(commit) for commit in Repo(test_repo / 'ondivi-test-repo').iter_commits())


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
def file_with_violations(test_repo: Path) -> Path:
    """File contain violations from linter."""
    violations_file = test_repo / 'violations.txt'
    violations_file.write_text(
        '\n'.join([
            '{0}:3:1: E302 expected 2 blank lines, found 1',
            '{0}:9:1: E302 expected 2 blank lines, found 1',
            '{0}:10:80: E501 line too long (123 > 79 characters)',
            '{0}:12:80: E501 line too long (119 > 79 characters)',
            '{0}:14:1: E305 expected 2 blank lines after class or function definition, found 1',
        ]).format(Path('inner/file.py')),
        encoding='utf-8',
    )
    return violations_file


@pytest.mark.usefixtures('test_repo')
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
def test_dependency_versions(version: tuple[str], run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test script with different dependency versions."""
    subprocess.run([str(bin_dir / 'pip'), 'install', *version], check=True)
    got = run_shell(
        [str(bin_dir / 'flake8'),
        str(Path('inner/file.py'))], [str(bin_dir / 'ondivi')],
    )

    assert got.stdout.decode('utf-8').strip() == '{0}:12:80: E501 line too long (119 > 79 characters)'.format(
        Path('inner/file.py'),
    )
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test(run_shell: _RUN_SHELL_T, revisions: tuple[str, ...], bin_dir: Path) -> None:
    """Test script with real git repo."""
    got = run_shell(
        [str(bin_dir / 'flake8'), str(Path('inner/file.py'))],
        [str(bin_dir / 'ondivi'), '--baseline', revisions[-1]],
    )

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        '{0}:3:1: E302 expected 2 blank lines, found 1'.format(Path('inner/file.py')),
        '{0}:9:1: E302 expected 2 blank lines, found 1'.format(Path('inner/file.py')),
        '{0}:12:80: E501 line too long (119 > 79 characters)'.format(Path('inner/file.py')),
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_baseline_default(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test baseline default."""
    got = run_shell([str(bin_dir / 'flake8'), str(Path('inner/file.py'))], [str(bin_dir / 'ondivi')])

    assert got.stdout.decode('utf-8').strip() == '{0}:12:80: E501 line too long (119 > 79 characters)'.format(
        Path('inner/file.py'),
    )
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_ruff(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test ruff."""
    got = run_shell(
        [str(bin_dir / 'ruff'), 'check', '--select=ALL', str(Path('inner/file.py')), '--output-format=concise'],
        [str(bin_dir / 'ondivi')],
    )

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        '{0}:12:5: T201 `print` found'.format(Path('inner/file.py')),
        '{0}:12:11: Q000 [*] Single quotes found but double quotes preferred'.format(Path('inner/file.py')),
        '{0}:12:89: E501 Line too long (119 > 88)'.format(Path('inner/file.py')),
        '{0}:16:16: Q000 [*] Single quotes found but double quotes preferred'.format(Path('inner/file.py')),
        '{0}:16:23: Q000 [*] Single quotes found but double quotes preferred'.format(Path('inner/file.py')),
        'Found 18 errors.',
        '[*] 8 fixable with the `--fix` option (4 hidden fixes can be enabled with the `--unsafe-fixes` option).',
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_mypy(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test mypy."""
    got = run_shell([str(bin_dir / 'mypy'), str(Path('inner/file.py'))], [str(bin_dir / 'ondivi')])

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        '{0}:16: error: Argument 2 to "User" has incompatible type "str"; expected "int"  [arg-type]'.format(
            Path('inner/file.py'),
        ),
        'Found 2 errors in 1 file (checked 1 source file)',
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
@pytest.mark.skipif(sys.platform.startswith('win'), reason='win not support "echo"')
def test_without_violations(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test exit without violations."""
    got = run_shell(['echo', ''], [str(bin_dir / 'ondivi')])

    assert got.returncode == 0


@pytest.mark.usefixtures('test_repo')
@pytest.mark.skipif(sys.platform.startswith('win'), reason='win not support "echo"')
def test_info_message(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test exit with info message."""
    got = run_shell(['echo', 'All files correct!'], [str(bin_dir / 'ondivi')])

    assert got.stdout.decode('utf-8').strip() == 'All files correct!'
    assert got.returncode == 0


@pytest.mark.usefixtures('test_repo')
@pytest.mark.skipif(sys.platform.startswith('win'), reason='win not support "echo"')
def test_format(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test with custom format."""
    got = run_shell(
        ['echo', 'line=12 file={0} message=`print` found'.format(Path('inner/file.py'))],
        [str(bin_dir / 'ondivi'), '--format', 'line={line_num:d} file={filename} {other}'],
    )

    assert got.stdout.decode('utf-8').strip() == 'line=12 file={0} message=`print` found'.format(Path('inner/file.py'))
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_click_app() -> None:
    """Test click app."""
    got = CliRunner().invoke(
        main,
        input='\n'.join([
            '{0}:3:1: E302 expected 2 blank lines, found 1',
            '{0}:9:1: E302 expected 2 blank lines, found 1',
            '{0}:10:80: E501 line too long (123 > 79 characters)',
            '{0}:12:80: E501 line too long (119 > 79 characters)',
            '{0}:14:1: E305 expected 2 blank lines after class or function definition, found 1',
        ]).format(Path('inner/file.py')),
    )

    assert got.exit_code == 1
    assert got.stdout.strip() == '{0}:12:80: E501 line too long (119 > 79 characters)'.format(Path('inner/file.py'))


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


@pytest.mark.usefixtures('test_repo')
def test_only_violations(run_shell: _RUN_SHELL_T, bin_dir: Path) -> None:
    """Test only violations."""
    got = run_shell(
        [str(bin_dir / 'ruff'), 'check', '--select=ALL', str(Path('inner/file.py')), '--output-format=concise'],
        [str(bin_dir / 'ondivi'), '--only-violations'],
    )

    assert got.stdout.decode('utf-8').strip().splitlines() == [
        '{0}:12:5: T201 `print` found'.format(Path('inner/file.py')),
        '{0}:12:11: Q000 [*] Single quotes found but double quotes preferred'.format(Path('inner/file.py')),
        '{0}:12:89: E501 Line too long (119 > 88)'.format(Path('inner/file.py')),
        '{0}:16:16: Q000 [*] Single quotes found but double quotes preferred'.format(Path('inner/file.py')),
        '{0}:16:23: Q000 [*] Single quotes found but double quotes preferred'.format(Path('inner/file.py')),
    ]
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_fromfile(file_with_violations: Path, bin_dir: Path) -> None:
    """Test script with violations from file."""
    got = subprocess.run(
        [str(bin_dir / 'ondivi'), '--fromfile', str(file_with_violations)],
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == '{0}:12:80: E501 line too long (119 > 79 characters)'.format(
        Path('inner/file.py'),
    )
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_fromfile_via_cli_runner(file_with_violations: Path) -> None:
    """Test script with violations from file via CliRunner."""
    got = CliRunner().invoke(main, ['--fromfile', str(file_with_violations)], input='')

    assert got.stdout.strip() == '{0}:12:80: E501 line too long (119 > 79 characters)'.format(Path('inner/file.py'))
    assert got.exit_code == 1


@pytest.mark.usefixtures('test_repo')
def test_fromfile_not_found(bin_dir: Path) -> None:
    """Test script with violations from file."""
    got = subprocess.run(
        [str(bin_dir / 'ondivi'), '--fromfile', 'undefined.txt'],
        stdout=subprocess.PIPE,
        check=False,
    )

    assert got.stdout.decode('utf-8').strip() == 'File with violations "undefined.txt" not found'
    assert got.returncode == 1


@pytest.mark.usefixtures('test_repo')
def test_fromfile_not_found_via_cli_runner() -> None:
    """Test script with violations from file via CliRunner."""
    got = CliRunner().invoke(main, ['--fromfile', 'undefined.txt'], input='')

    assert got.stdout == 'File with violations "undefined.txt" not found\n'
    assert got.exit_code == 1


@pytest.mark.usefixtures('test_repo')
def test_commit_not_found() -> None:
    """Test commit not found."""
    got = CliRunner().invoke(main, ['--baseline', 'fakeHash'], input='')

    assert got.stdout == 'Revision "fakeHash" not found'
    assert got.exit_code == 1
