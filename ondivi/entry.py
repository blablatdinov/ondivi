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
    only_violations: bool,
) -> tuple[ActualViolationsListStr, bool]:
    """Entrypoint.

    :param diff: Diff
    :param violations: list[str]
    :param violation_format: ViolationFormatStr
    :param only_violations: bool
    :return: tuple[ActualViolationsListStr, bool]
    """
    return filter_out_violations(define_changed_lines(diff), violations, violation_format, only_violations)


def cli(baseline: str, violation_format: str, only_violations: bool) -> None:
    """Controller with CLI side effects.

    :param baseline: str
    :param violation_format: str
    :param only_violations: bool
    """
    filtered_lines, violation_found = controller(
        Repo('.').git.diff('--unified=0', baseline),
        sys.stdin.read().strip().splitlines(),
        violation_format,
        only_violations,
    )
    sys.stdout.write('\n'.join(filtered_lines))
    sys.stdout.write('\n')
    if violation_found:
        sys.exit(1)


# print('\n'.join([
#         'Template for parsing linter messages. The template should include the following named parts:',
#         '{filename}   The name of the file with the error/warning',
#         '{line_num}   The line number with the error/warning (integer)',
#         'Example usage:',
#         '--format "{filename}:{line_num:d}{other}"',
#         'In this example, the linter message',
#         '"src/app_types/listable.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`"',
#         'will be recognized and parsed into the following components:',
#         ' - filename: "src/app_types/listable.py"',
#         ' - line_num: 23',
#         ' - other: :1: UP035 Import from `collections.abc` instead: `Sequence`"',
#         'Ensure that the template matches the format of the messages generated by your linter.',
#         '(default: "{filename}:{line_num:d}{other}")',
#     ]))


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
    help='\b\n{0}'.format('\n'.join([
        'Template for parsing linter messages. The template should include the following named parts:',
        '{filename}   The name of the file with the error/warning',
        '{line_num}   The line number with the error/warning (integer)',
        'Example usage:',
        '--format "{filename}:{line_num:d}{other}"',
        'In this example, the linter message',
        '"src/app_types/listable.py:23:1: UP035 Import from collections.abc instead: Sequence"',
        'will be recognized and parsed into the following components:',
        ' - filename: "src/app_types/listable.py"',
        ' - line_num: 23',
        ' - other: :1: UP035 Import from collections.abc instead: Sequence"',
        'Ensure that the template matches the format of the messages generated by your linter.',
        '(default: "{filename}:{line_num:d}{other}")',
    ])),
)
@click.option(
    '--only-violations',
    default=False,
    help='Show only violations',
    is_flag=True,
)
def main(baseline: str, violation_format: str, only_violations: bool) -> None:
    """Ondivi (Only diff violations).

    Python script filtering coding violations, identified by static analysis,
    only for changed lines in a Git repo.
    Usage example:

    flake8 script.py | ondivi
    """
    try:
        cli(baseline, violation_format, only_violations)
    except Exception as err:  # noqa: BLE001. Application entrypoint
        sys.stdout.write('\n'.join([
            'Ondivi fail with: "{0}"'.format(err),
            'Please submit it to https://github.com/blablatdinov/ondivi/issues',
            'Copy and paste this stack trace to GitHub:',
            '========================================',
            traceback.format_exc(),
        ]))
        sys.exit(1)
