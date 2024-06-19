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

import sys
import traceback

import click
from git import Repo

from ondivi.define_changed_lines import define_changed_lines
from ondivi.filter_out_violations import filter_out_violations
from ondivi.types import ActualViolationsListStr, DiffStr, ViolationFormatStr


def controller(
    diff: DiffStr,
    violations: list[str],
    violation_format: ViolationFormatStr,
) -> tuple[ActualViolationsListStr, bool]:
    """Entrypoint.

    :param diff: Diff
    :param violations: list[str]
    :param violation_format: ViolationFormatStr
    :return: tuple[ActualViolationsListStr, bool]
    """
    changed_lines = define_changed_lines(diff)
    return filter_out_violations(changed_lines, violations, violation_format)


def cli(baseline: str, violation_format: str) -> None:
    """Controller with CLI side effects.

    :param baseline: str
    :param violation_format: str
    """
    filtered_lines, violation_found = controller(
        Repo('.').git.diff('--unified=0', baseline),
        sys.stdin.read().strip().splitlines(),
        violation_format,
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
    '--format',
    'violation_format',
    default='{filename}:{line_num:d}{other}',
    help='\n'.join([
        'Template for parsing linter messages. The template should include the following named parts:\n',
        '{filename}   The name of the file with the error/warning',
        '{line_num}   The line number with the error/warning (integer)\n',
        'Example usage:',
        '--format "{filename}:{line_num:d}{other}"\n',
        ' '.join([
            'In this example, the linter message',
            '"src/app_types/listable.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`"\n',
        ]),
        'will be recognized and parsed into the following components:\n',
        ' - filename: "src/app_types/listable.py"\n',
        ' - line_num: 23\n',
        ' - other: :1: UP035 Import from `collections.abc` instead: `Sequence`"\n',
        'Ensure that the template matches the format of the messages generated by your linter.\n',
        '(default: "{filename}:{line_num:d}{other}")',
    ]),
)
def main(baseline: str, violation_format: str) -> None:
    """Ondivi (Only diff violations).

    Python script filtering coding violations, identified by static analysis,
    only for changed lines in a Git repo.
    Usage example:

    flake8 script.py | ondivi
    """
    try:
        cli(baseline, violation_format)
    except Exception as err:  # noqa: BLE001. Application entrypoint
        sys.stdout.write('\n'.join([
            'Ondivi fail with: "{0}"'.format(err),
            'Please submit it to https://github.com/blablatdinov/ondivi/issues',
            'Copy and paste this stack trace to GitHub:',
            '========================================',
            traceback.format_exc(),
        ]))
        sys.exit(1)
