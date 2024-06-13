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

from ondivi.__main__ import controller


def test_controller() -> None:
    """Testing script output with diff and violations list."""
    got, found = controller(
        Path('tests/fixtures/diff.txt').read_text(),
        Path('tests/fixtures/violations.txt').read_text().splitlines(),
        '{filename}:{line_num:d}:{col_num:d}: {message}',
    )

    assert got == [
        'src/app_types/listable.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`',
        'src/srv/ayats/ayats_by_text_query.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`',
        'src/srv/ayats/ayats_by_text_query.py:23:47: F401 [*] `typing.Generic` imported but unused',
        'src/srv/ayats/favorite_ayats_after_remove.py:23:1: UP035 Import from `collections.abc` instead: `Sequence`',
        ' '.join([
            'src/srv/ayats/pg_ayat.py:64:30: PLR2004 Magic value used in comparison,',
            'consider replacing `4096` with a constant variable',
        ]),
        'src/srv/ayats/pg_ayat.py:66:44: COM812 Trailing comma missing',
        ' '.join([
            "src/tests/it/srv/ayats/test_pg_ayat.py:78:19: PLC1901 `got == ''` can be simplified",
            'to `not got` as an empty string is falsey',
        ]),
        'src/app_types/listable.py:33:20: PYI059 `Generic[]` should always be the last base class',
        ' '.join([
            'src/tests/it/srv/ayats/test_pg_ayat.py:90:13: PLW1514 `pathlib.Path(...).read_text`',
            'without explicit `encoding` argument',
        ]),
        ' '.join([
            'src/tests/it/srv/ayats/test_pg_ayat.py:95:19: PLW1514 `pathlib.Path(...).read_text`',
            'without explicit `encoding` argument',
        ]),
    ]
    assert found
