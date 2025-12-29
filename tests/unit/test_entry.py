# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Tests for ondivi."""

from typing import Callable

from ondivi.entry import controller


def test_controller(localize_violation_path: Callable[[str], str]) -> None:
    """Testing script output with diff and violations list."""
    got, found = controller(
        '\n'.join([
            'diff --git a/ondivi/__main__.py b/ondivi/__main__.py',
            'index 669d0ff..7a518fa 100644',
            '--- a/ondivi/__main__.py',
            '+++ b/ondivi/__main__.py',
            '@@ -26,0 +27,1 @@ from git import Repo',
            '+Diff = str',
        ]),
        [localize_violation_path('ondivi/__main__.py:27:1: Error message')],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert got == [localize_violation_path('ondivi/__main__.py:27:1: Error message')]
    assert found
