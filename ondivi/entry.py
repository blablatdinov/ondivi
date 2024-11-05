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

"""Ondivi (Only diff violations).

Python script filtering coding violations, identified by static analysis,
only for changed lines in a Git repo.
"""

# flake8: noqa: WPS436. _internal allow into ondivi app

from __future__ import annotations

import sys
import traceback
from pathlib import Path

import click
from git import Repo
from git.exc import GitCommandError

from ondivi._internal.define_changed_lines import define_changed_lines
from ondivi._internal.filter_out_violations import filter_out_violations
from ondivi._internal.types import (
    ActualViolationsListStr,
    BaselineStr,
    DiffStr,
    FromFilePathStr,
    LinterAdditionalMessageStr,
    ViolationFormatStr,
    ViolationStr,
)


def controller(
    diff: DiffStr,
    linter_out: list[ViolationStr | LinterAdditionalMessageStr],
    violation_format: ViolationFormatStr,
    only_violations: bool,
) -> tuple[ActualViolationsListStr, bool]:
    """Entrypoint.

    :param diff: Diff
    :param linter_out: list[str]
    :param violation_format: ViolationFormatStr
    :param only_violations: bool
    :return: tuple[ActualViolationsListStr, bool]
    """
    return filter_out_violations(
        define_changed_lines(diff),
        linter_out,
        violation_format,
        only_violations,
    )


def _linter_output_from_file(file_path: FromFilePathStr) -> list[str]:
    if not Path(file_path).exists():
        sys.stdout.write('File with violations "{0}" not found\n'.format(file_path))
        sys.exit(1)
    return Path(file_path).read_text(encoding='utf-8').strip().splitlines()


def cli(
    baseline: BaselineStr,
    fromfile: FromFilePathStr | None,
    violation_format: ViolationFormatStr,
    only_violations: bool,
) -> None:
    """Controller with CLI side effects.

    :param baseline: BaselineStr
    :param fromfile: FromFilePathStr | None
    :param violation_format: ViolationFormatStr
    :param only_violations: bool
    """
    linter_output = _linter_output_from_file(fromfile) if fromfile else sys.stdin.read().strip().splitlines()
    try:
        diff = Repo('.').git.diff('--unified=0', baseline)
    except GitCommandError:
        sys.stdout.write('Revision "{0}" not found'.format(baseline))
        sys.exit(1)
    filtered_lines, violation_found = controller(
        diff,
        linter_output,
        violation_format,
        only_violations,
    )
    sys.stdout.write('\n'.join(filtered_lines))
    sys.stdout.write('\n')
    if violation_found:
        sys.exit(1)


# flake8: noqa: DAR101. Broke --help out
@click.command()
@click.option(
    '--baseline',
    default='master',
    help=' '.join([
        'Commit or branch which will contain legacy code.',
        'Program filter out violations on baseline',
        '(default: "master")',
    ]),
)
@click.option(
    '--fromfile',
    default=None,
    help='Path to file with violations. Expected "utf-8" encoding',
)
@click.option(
    '--format',
    'violation_format',
    default='{filename}:{line_num:d}{other}',
    help=''.join([
        'Template for parsing linter messages. The template should include the following named parts:\n\n',
        '{filename}   The name of the file with the error/warning\n',
        '{line_num}   The line number with the error/warning (integer)\n\n',
        'Example usage:\n\n',
        '--format "{filename}:{line_num:d}{other}"\n\n',
        'In this example, the linter message\n\n',
        '"src/app_types/listable.py:23:1: UP035 Import from collections.abc instead: Sequence"\n\n',
        'will be recognized and parsed into the following components:\n\n',
        ' - filename: "src/app_types/listable.py"\n\t\t\t\t',
        ' - line_num: 23\n\t\t\t\t\t',
        ' - other: :1: "UP035 Import from collections.abc instead: Sequence"\n\n',
        'Ensure that the template matches the format of the messages generated by your linter.\n\t\t\t\t',
        '(default: "{filename}:{line_num:d}{other}")',
    ]),
)
@click.option(
    '--only-violations',
    default=False,
    help='Show only violations',
    is_flag=True,
)
def main(baseline: str, fromfile: str | None, violation_format: str, only_violations: bool) -> None:
    """Ondivi (Only diff violations).

    Python script filtering coding violations, identified by static analysis,
    only for changed lines in a Git repo.
    Usage example:

    flake8 script.py | ondivi
    """
    try:
        cli(baseline, fromfile, violation_format, only_violations)
    except Exception as err:  # noqa: BLE001. Application entrypoint
        sys.stdout.write('\n'.join([
            'Ondivi fail with: "{0}"'.format(err),
            'Please submit it to https://github.com/blablatdinov/ondivi/issues',
            'Copy and paste this stack trace to GitHub:',
            '========================================',
            traceback.format_exc(),
        ]))
        sys.exit(1)
