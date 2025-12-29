# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Tests for ondivi."""

# _internal allow into ondivi app
from ondivi._internal.filter_out_violations import filter_out_violations  # noqa: WPS436


def test_without_violation() -> None:
    """Test filtering without violations."""
    violations, found = filter_out_violations(
        {},
        ['All checks passed'],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert violations == ['All checks passed']
    assert not found


def test_custom_format() -> None:
    """Test custom violation format."""
    violations, found = filter_out_violations(
        {'file.py': [12]},
        ['line=12 file=file.py message=`print` found'],
        'line={line_num:d} file={filename} {other}',
        only_violations=False,
    )

    assert violations == ['line=12 file=file.py message=`print` found']
    assert found


def test_not_target_violation() -> None:
    """Test not target violation."""
    violations, found = filter_out_violations(
        {'file.py': [1, 2]},
        ['file.py:3:1: line too long'],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert not violations
    assert not found


def test_file_without_diff() -> None:
    """Test file without diff."""
    violations, found = filter_out_violations(
        {'file.py': [1, 2]},
        ['foo.py:3:1: line too long'],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert not violations
    assert not found


def test_only_violations() -> None:
    """Test only violations."""
    violations, found = filter_out_violations(
        {'file.py': [3]},
        [
            'file.py:3:1: line too long',
            'Info message',
        ],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=True,
    )

    assert violations == ['file.py:3:1: line too long']
    assert found


def test_path_starts_with_dot() -> None:
    """Test path starts with dot."""
    violations, found = filter_out_violations(
        {'file.py': [3]},
        ['./file.py:3:1: line too long'],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert violations == ['./file.py:3:1: line too long']
    assert found
