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

"""Define changed lines in file."""

from ondivi._internal.types import DiffStr, FileNameStr  # noqa: WPS436. _internal allow into ondivi app


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
    changed_lines: dict[FileNameStr, list[int]] = {}
    current_file = ''
    for line in diff.splitlines():
        if _line_contain_filename(line):
            current_file = line.split(' b/')[-1].strip()
            changed_lines[current_file] = []
        elif _diff_line_contain_changed_lines(line):
            changed_lines[current_file].extend(_changed_lines(line))
    return changed_lines


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
