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
import sys

from git import Repo
from parse import parse as parse_from_pattern

DiffStr = str
FileNameStr = str
ActualViolationsListStr = list[str]
ViolationFormatStr = str


def define_changed_lines(diff: DiffStr) -> dict[FileNameStr, list[int]]:
    """Define changed lines in file.

    Example of diff:

    +---------------------------------------------------------------------+
    │ diff --git a/ondivi/__main__.py b/ondivi/__main__.py                | <- filename
    | index 669d0ff..7a518fa 100644                                       |
    | --- a/ondivi/__main__.py                                            |
    | +++ b/ondivi/__main__.py                                            |
    | @@ -26,0 +27,2 @@ from git import Repo                              | <- Changed lines = [27, 28]
    | +Diff = str                                                         |
    | +FileName = str                                                     |
    | @@ -28 +30,2 @@ from git import Repo                                | <- Changed lines = [27, 28, 30, 31]
    | -def define_changed_lines(diff):                                    |
    | +                                                                   |
    | +def define_changed_lines(diff: Diff) -> dict[FileName, list[int]]: |
    +---------------------------------------------------------------------+

    :param diff: DiffStr
    :return: dict[FileNameStr, list[int]]
    """
    res: dict[FileNameStr, list[int]] = {}
    current_file = ''
    for line in diff.splitlines():
        if _line_contain_filename(line):
            current_file = line.split(' b/')[-1].strip()
            res[current_file] = []
        elif _diff_line_contain_changed_lines(line):
            res[current_file].extend(_changed_lines(line))
    return res


def _line_contain_filename(diff_line: str) -> bool:
    return diff_line.startswith('diff --git')


def _diff_line_contain_changed_lines(diff_line: str) -> bool:
    return diff_line.startswith('@@')


def _changed_lines(diff_line: str) -> list[int]:
    """Changed lines.

    >>> _changed_lines('@@ -28 +30,2 @@ from git import Repo')
    [30, 31]

    :param diff_line: str
    :return: list[int]
    """
    splitted_line = diff_line.split('@@')[1].strip()
    added_lines = splitted_line.split('+')[1]
    start_line = int(
        added_lines.split(',')[0],
    )
    num_lines = 0
    if ',' in added_lines:
        num_lines = int(added_lines.split(',')[1]) - 1
    return list(range(
        start_line, start_line + num_lines + 1,
    ))


def filter_out_violations(
    changed_lines: dict[FileNameStr, list[int]],
    violations: list[str],
    violation_format: ViolationFormatStr,
) -> tuple[ActualViolationsListStr, bool]:
    """Collect target violations.

    :param changed_lines: dict[FileName, list[int]], violations: list[str]
    :param violations: list[str]
    :param violation_format: ViolationFormatStr
    :return: tuple[ActualViolationsListStr, bool]
    """
    res = []
    violation_found = False
    for violation in violations:
        line_for_out, is_violation = _is_line_for_out(changed_lines, violation, violation_format)
        violation_found = violation_found or is_violation
        if line_for_out:
            res.append(violation)
    return res, violation_found


def _is_line_for_out(
    changed_lines: dict[FileNameStr, list[int]],
    violation: list[str],
    violation_format: ViolationFormatStr,
) -> tuple[bool, bool]:
    parsed_violation = parse_from_pattern(violation_format, violation)
    line_for_out, is_violation = True, True
    if not parsed_violation:
        line_for_out = True
        is_violation = False
    elif (
        parsed_violation['filename'] not in changed_lines
        or parsed_violation['line_num'] not in changed_lines[parsed_violation['filename']]
    ):
        line_for_out = False
        is_violation = False
    return line_for_out, is_violation


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
            '{col_num}    The column number with the error/warning (integer)',
            '{error_code} The linter error/warning code',
            '{message}    The linter message\n',
            'Example usage:',
            '--format "{filename}:{line_num:d}:{col_num:d}: {error_code} {message}"\n',
            ' '.join([
                'In this example, the linter message',
                '"src/app_types/listable.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`"',
            ]),
            'will be recognized and parsed into the following components:',
            '- filename: "src/app_types/listable.py"',
            '- line_num: 23',
            '- col_num: 1',
            '- error_code: "UP035"',
            '- message: "Import from `collections.abc` instead: `Sequence`"\n',
            'Ensure that the template matches the format of the messages generated by your linter.',
        ]),
    )
    args = parser.parse_args()
    filtered_lines, violation_found = controller(
        Repo('.').git.diff('--unified=0', args.baseline),
        sys.stdin.read().strip().splitlines(),
        args.violation_format,
    )
    sys.stdout.write('\n'.join(filtered_lines))
    sys.stdout.write('\n')
    if violation_found:
        sys.exit(1)


if __name__ == '__main__':
    main()
