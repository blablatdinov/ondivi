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

from ondivi.entry import controller


def test_controller() -> None:
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
        ['ondivi/__main__.py:27:1: Error message'],
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert got == ['ondivi/__main__.py:27:1: Error message']
    assert found
