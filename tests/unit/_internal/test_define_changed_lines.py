# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Tests for ondivi."""

from pathlib import Path
from typing import Callable

# _internal allow into ondivi app
from ondivi._internal.define_changed_lines import define_changed_lines  # noqa: WPS436


def test_define_changed_files(localize_violation_path: Callable[[str], str]) -> None:
    """Testing search changed lines."""
    got = define_changed_lines(
        Path('tests/fixtures/diff.patch').read_text(encoding='utf-8'),
    )

    assert got == {
        localize_violation_path('django/db/models/sql/query.py'): [
            *range(1367, 1374),
            *range(1401, 1408),
            *range(1418, 1432),
        ],
        localize_violation_path('tests/custom_lookups/tests.py'): list(range(614, 624)),
        localize_violation_path('tests/lookup/tests.py'): [
            *range(812, 846),
            *range(853, 860),
            *range(1087, 1097),
        ],
    }


def test_define_filename() -> None:
    """Test define filename.

    Created for kill mutant
    """
    got = define_changed_lines(
        'diff --git XX b/ XX b/ file.py',
    )

    assert got == {'file.py': []}
