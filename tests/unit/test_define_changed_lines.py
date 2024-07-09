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

from pathlib import Path

from ondivi._internal.define_changed_lines import define_changed_lines


def test_define_changed_files() -> None:
    """Testing search changed lines."""
    got = define_changed_lines(
        Path('tests/fixtures/diff.patch').read_text(encoding='utf-8'),
    )

    assert got == {
        'django/db/models/sql/query.py': [
            *range(1367, 1374),
            *range(1401, 1408),
            *range(1418, 1432),
        ],
        'tests/custom_lookups/tests.py': list(range(614, 624)),
        'tests/lookup/tests.py': [
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
