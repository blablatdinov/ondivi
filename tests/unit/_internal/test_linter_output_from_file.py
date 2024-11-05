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

"""Tests read violations from file."""

import uuid
from pathlib import Path

import pytest

# _internal allow into ondivi app
from ondivi._internal.linter_output_from_file import linter_output_from_file  # noqa: WPS436


@pytest.fixture
def violations() -> list[str]:
    return [
        'django/db/models/sql/query.py:1404:9: ANN201 Missing return type annotation for public function `try_transform`',
        'django/db/models/sql/query.py:1404:29: ANN001 Missing type annotation for function argument `lhs`',
        'django/db/models/sql/query.py:1404:34: ANN001 Missing type annotation for function argument `name`',
    ]


@pytest.fixture
def file(tmp_path: Path, violations: list[str]) -> Path:
    path = tmp_path / 'file.txt'
    path.write_text('\n'.join(violations))
    return path


def test_linter_out_from_file(file: Path, violations: list[str]) -> None:
    """Test read violations from file."""
    got = linter_output_from_file(file)

    assert got == violations


def test_file_not_found() -> None:
    """Test file not found."""
    with pytest.raises(FileNotFoundError):
        linter_output_from_file('/{0}'.format(uuid.uuid4()))
