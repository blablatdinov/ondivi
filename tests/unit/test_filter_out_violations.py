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

"""Tests for ondivi."""

import pytest

from ondivi.filter_out_violations import filter_out_violations


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
            'foo.py:3:1: line too long',
            'Info message',
        ],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=True,
    )

    assert violations == ['foo.py:3:1: line too long']
    assert found
