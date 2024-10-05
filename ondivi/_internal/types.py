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

"""Ondivi app types."""

from typing import TypedDict

DiffStr = str
# Diff str is out of `git diff` command
# Example:
# +---------------------------------------------------------------------+
# │ diff --git a/ondivi/__main__.py b/ondivi/__main__.py                |
# | index 669d0ff..7a518fa 100644                                       |
# | --- a/ondivi/__main__.py                                            |
# | +++ b/ondivi/__main__.py                                            |
# | @@ -26,0 +27,2 @@ from git import Repo                              |
# | +Diff = str                                                         |
# | +FileName = str                                                     |
# | @@ -28 +30,2 @@ from git import Repo                                |
# | -def define_changed_lines(diff):                                    |
# | +                                                                   |
# | +def define_changed_lines(diff: Diff) -> dict[FileName, list[int]]: |
# +---------------------------------------------------------------------+

FileNameStr = str
# Filename with path to file
# This name must be equal in git diff and linter out

ViolationStr = str
# One line of violation output
# Example:
# "src/app_types/listable.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`""

LinterAdditionalMessageStr = str
# Some additional messages from checkers which not contain code violation
# For example ruff write to stdout "Found 17 errors."
# This line not needed for ondivi, but we must send it to user in some cases
# See: "--only-violations" option

ActualViolationsListStr = list[str]
# List of violations filtered by ondivi

ViolationFormatStr = str
# Template for parsing linter messages. The template should include the following named parts:',
# {filename}   The name of the file with the error/warning',
# {line_num}   The line number with the error/warning (integer)',
# See "--format" option, https://github.com/r1chardj0n3s/parse

BaselineStr = str
# Branch name or commit hash

FromFilePathStr = str
# Path to file with violations in utf-8 encoding


class ParsedViolation(TypedDict):
    """Parsed violation.

    After parsing parse.parse takes dict type
    """

    filename: FileNameStr
    line_num: int
