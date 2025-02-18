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

"""Tests for ondivi."""

from pathlib import Path
from typing import Callable

from ondivi.entry import controller


def test_controller(localize_violation_path: Callable[[str], str]) -> None:
    """Testing script output with diff and violations list."""
    got, found = controller(
        Path('tests/fixtures/diff.patch').read_text(encoding='utf-8'),
        [
            localize_violation_path(line)
            for line in Path('tests/fixtures/violations.txt').read_text(encoding='utf-8').splitlines()
        ],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert got == [
        localize_violation_path(line)
        for line in Path('tests/fixtures/actual_violations.txt').read_text(encoding='utf-8').splitlines()
    ]
    assert found
