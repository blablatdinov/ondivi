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
from contextlib import suppress

from git import Repo

Diff = str
FileName = str


def define_changed_lines(diff: Diff) -> dict[FileName, list[int]]:  # noqa: WPS210. TODO: too many local variables
    """Define changed lines in file.

    :param diff: Diff
    :return: dict[FileName, list[int]]
    """
    res: dict[FileName, list[int]] = {}
    current_file = ''
    for line in diff.splitlines():
        if line.startswith('diff --git'):
            current_file = line.split(' b/')[-1].strip()
            res[current_file] = []
        elif line.startswith('@@'):
            splitted_line = line.split('@@')[1].strip()
            added_lines = splitted_line.split('+')[1]
            start_line = int(
                added_lines.split(',')[0],
            )
            if ',' not in added_lines:  # noqa: SIM108. Too complexity line
                num_lines = 0
            else:
                num_lines = int(added_lines.split(',')[1]) - 1
            res[current_file].extend(list(range(
                start_line, start_line + num_lines + 1,
            )))
    return res


def filter_out_violations(
    changed_lines: dict[FileName, list[int]],
    violations: list[str],
) -> list[str]:
    """Collect target violations.

    :param changed_lines: dict[FileName, list[int]], violations: list[str]
    :param violations: list[str]
    :return: list[str]
    """
    res = []
    for violation in violations:
        with suppress(ValueError, IndexError):
            filename = violation.split(':')[0]
            line = int(violation.split(':')[1])
            if filename not in changed_lines:
                continue
            if line not in changed_lines[filename]:
                continue
        res.append(violation)
    return res


def controller(diff: Diff, violations: list[str]) -> list[str]:
    """Entrypoint.

    :param diff: Diff
    :param violations: list[str]
    :return: list[str]
    """
    changed_lines = define_changed_lines(diff)
    return filter_out_violations(changed_lines, violations)


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
    args = parser.parse_args()
    violations = sys.stdin.read().strip().splitlines()
    sys.stdout.write('\n'.join(
        controller(
            Repo('.').git.diff('--unified=0', args.baseline),
            violations,
        ),
    ))
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
