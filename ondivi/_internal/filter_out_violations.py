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

"""Collect target violations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from parse import parse as parse_from_pattern  # type: ignore [import-untyped]

from ondivi._internal.ondivi_types import (  # noqa: WPS436. _internal allow into ondivi app
    ActualViolationsListStr,
    FileNameStr,
    LinterAdditionalMessageStr,
    ParsedViolation,
    ViolationFormatStr,
    ViolationStr,
)


@dataclass(frozen=True)
class LinterOutLine:

    _raw_line: ViolationStr | LinterAdditionalMessageStr
    _violation_format: ViolationFormatStr

    def line_num(self) -> int:
        return self._parse()['line_num']

    def filename(self) -> str:
        return str(Path(
            self._parse()['filename']
            .replace('./', '')
            .replace('\\', '/'),
        ))

    def violation_exist(self) -> bool:
        return bool(self._parse())

    def _parse(self) -> ParsedViolation:
        prsd: ParsedViolation = parse_from_pattern(self._violation_format, self._raw_line)
        return prsd


def filter_out_violations(
    changed_lines: dict[FileNameStr, list[int]],
    linter_out: list[ViolationStr | LinterAdditionalMessageStr],
    violation_format: ViolationFormatStr,
    only_violations: bool,
) -> tuple[ActualViolationsListStr, bool]:
    """Collect target violations.

    :param changed_lines: dict[FileName, list[int]], violations: list[str]
    :param linter_out: list[ViolationStr | LinterAdditionalMessageStr]
    :param violation_format: ViolationFormatStr
    :param only_violations: bool
    :return: tuple[ActualViolationsListStr, bool]
    """
    filtered_violations = []
    violation_found = False
    for linter_out_line in linter_out:
        line_for_out, is_violation = _is_line_for_out(
            changed_lines,
            LinterOutLine(linter_out_line, violation_format),
        )
        violation_found = violation_found or is_violation
        if is_violation or (line_for_out and not only_violations):
            filtered_violations.append(linter_out_line)
    return filtered_violations, violation_found


def _is_line_for_out(
    changed_lines: dict[FileNameStr, list[int]],
    linter_out_line: LinterOutLine,
) -> tuple[bool, bool]:
    line_for_out, is_violation = True, True
    if not linter_out_line.violation_exist():
        line_for_out = True
        is_violation = False
    elif not _is_target_violation(changed_lines, linter_out_line):
        line_for_out = False
        is_violation = False
    return line_for_out, is_violation


def _is_target_violation(changed_lines: dict[FileNameStr, list[int]], linter_out_line: LinterOutLine) -> bool:
    violation_file = linter_out_line.filename()
    is_target_file = violation_file in changed_lines
    try:
        violation_on_changed_line = linter_out_line.line_num() in changed_lines[violation_file]
    except KeyError:
        violation_on_changed_line = False
    return is_target_file and violation_on_changed_line
