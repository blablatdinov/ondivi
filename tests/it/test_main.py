# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Tests for ondivi."""

from collections.abc import Callable
from pathlib import Path

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
