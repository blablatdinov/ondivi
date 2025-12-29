# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
