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

import argparse
import traceback
import sys
from typing import TextIO, Callable

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


def cli(args):
    filtered_lines, violation_found = controller(
        Repo('.').git.diff('--unified=0', args.baseline),
        sys.stdin.read().strip().splitlines(),
        args.violation_format,
    )
    sys.stdout.write('\n'.join(filtered_lines))
    if violation_found:
        sys.stdout.write('\n')
        sys.exit(1)


def main() -> None:
    """Entrypoint."""
    parser = argparse.ArgumentParser(
        description='\n'.join([
            'Ondivi (Only diff violations).\n',
            'Python script filtering coding violations, identified by static analysis,',
            'only for changed lines in a Git repo.\n',
            'Usage example:\n',
            'flake8 script.py | ondivi',
        ]),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        '--baseline',
        dest='baseline',
        type=str,
        default='master',
        help=' '.join([
            'Commit or branch which will contain legacy code.',
            'Program filter out violations on baseline',
            '(default: "master")',
        ]),
    )
    parser.add_argument(
        '--format',
        dest='violation_format',
        type=str,
        default='{filename}:{line_num:d}{other}',
        help='\n'.join([
            'Template for parsing linter messages. The template should include the following named parts:\n',
            '{filename}   The name of the file with the error/warning',
            '{line_num}   The line number with the error/warning (integer)',
            'Example usage:',
            '--format "{filename}:{line_num:d}{other}"\n',
            ' '.join([
                'In this example, the linter message',
                '"src/app_types/listable.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`"',
            ]),
            'will be recognized and parsed into the following components:',
            '- filename: "src/app_types/listable.py"',
            '- line_num: 23',
            '- other: :1: UP035 Import from `collections.abc` instead: `Sequence`"\n',
            'Ensure that the template matches the format of the messages generated by your linter.\n',
            '(default: "{filename}:{line_num:d}{other}")',
        ]),
    )
    args = parser.parse_args()
    try:
        cli(args)
    except Exception as err:
        sys.stdout.write('\n'.join([
            'Fail with: "{0}"'.format(err),
            'Please submit it to https://github.com/blablatdinov/ondivi/issues',
            'Copy and paste this stack trace to GitHub:',
            '========================================',
            traceback.format_exc(),
        ]))
        sys.exit(1)


if __name__ == '__main__':
    main()
