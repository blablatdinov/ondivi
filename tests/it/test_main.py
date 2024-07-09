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

from ondivi.entry import controller


def test_controller() -> None:
    """Testing script output with diff and violations list."""
    got, found = controller(
        Path('tests/fixtures/diff.patch').read_text(encoding='utf-8'),
        Path('tests/fixtures/violations.txt').read_text(encoding='utf-8').splitlines(),
        '{filename}:{line_num:d}:{col_num:d}: {message}',
        only_violations=False,
    )

    assert got == [
        'django/db/models/sql/query.py:1404:9: ANN201 Missing return type annotation for public function `try_transform`', 'django/db/models/sql/query.py:1404:29: ANN001 Missing type annotation for function argument `lhs`', 'django/db/models/sql/query.py:1404:34: ANN001 Missing type annotation for function argument `name`', 'django/db/models/sql/query.py:1404:40: ANN001 Missing type annotation for function argument `lookups`', 'django/db/models/sql/query.py:1405:9: D205 1 blank line required between summary line and description', 'django/db/models/sql/query.py:1405:9: D212 [*] Multi-line docstring summary should start at the first line', 'django/db/models/sql/query.py:1405:9: D401 First line of docstring should be in imperative mood: "Helper method for build_lookup(). Try to fetch and initialize"', 'django/db/models/sql/query.py:1418:30: UP031 Use format specifiers instead of percent format', 'django/db/models/sql/query.py:1427:17: UP031 Use format specifiers instead of percent format', 'django/db/models/sql/query.py:1428:88: COM812 [*] Trailing comma missing', 'django/db/models/sql/query.py:1431:9: C901 `build_filter` is too complex (20 > 10)', 'django/db/models/sql/query.py:1431:9: PLR0913 Too many arguments in function definition (10 > 5)', 'django/db/models/sql/query.py:1431:9: PLR0912 Too many branches (21 > 12)', 'django/db/models/sql/query.py:1431:9: PLR0915 Too many statements (60 > 50)', 'django/db/models/sql/query.py:1431:9: ANN201 Missing return type annotation for public function `build_filter`', 'tests/custom_lookups/tests.py:623:13: PT009 Use a regular `assert` instead of unittest-style `assertEqual`', 'tests/lookup/tests.py:843:9: ANN201 Missing return type annotation for public function `test_unsupported_lookups_custom_lookups`', 'tests/lookup/tests.py:843:9: D102 Missing docstring in public method', 'tests/lookup/tests.py:844:22: SLF001 Private member accessed: `_meta`', 'tests/lookup/tests.py:853:9: ANN201 Missing return type annotation for public function `test_relation_nested_lookup_error`', 'tests/lookup/tests.py:853:9: D102 Missing docstring in public method',
    ]
    assert found
