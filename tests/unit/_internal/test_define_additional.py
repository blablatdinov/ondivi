# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test define additional violations."""

import pytest

from ondivi._internal.define_additional import define_additional
from ondivi._internal.exceptions import InvalidSizeError


def test() -> None:
    """Test define additional violations."""
    got = define_additional(
        [
            'django/db/models/sql/query.py:1:1: D212 [*] Multi-line docstring summary should start at the first line',
            ' '.join([
                'django/db/models/sql/query.py:60:5: ANN202 Missing return type annotation for private function',
                '`get_field_names_from_opts`',
            ]),
            'django/db/models/sql/query.py:60:31: ANN001 Missing type annotation for function argument `opts`',
            'django/db/models/sql/query.py:66:10: COM812 [*] Trailing comma missing',
            ' '.join([
                'django/db/models/sql/query.py:70:5: ANN202 Missing return type annotation for private function',
                '`get_paths_from_expression`',
            ]),
        ],
        [
            'django/db/models/sql/query.py:1:1: D212 [*] Multi-line docstring summary should start at the first line',
        ],
        2,
    )

    assert len(got) == 2
    assert got == [
        ' '.join([
            'django/db/models/sql/query.py:60:5: ANN202 Missing return type annotation for private function',
            '`get_field_names_from_opts`',
        ]),
        ' '.join([
            'django/db/models/sql/query.py:70:5: ANN202 Missing return type annotation for private function',
            '`get_paths_from_expression`',
        ]),
    ]


@pytest.mark.parametrize('size', [
    -1,
    0,
])
def test_invalid_size(size: int) -> None:
    """Test invalid size."""
    with pytest.raises(InvalidSizeError):
        define_additional(['1:1 violation'], ['1:1 violation'], size)


def test_size_greater_than_violations_count() -> None:
    """Test size greater than violations count."""
    got = define_additional(
        [
            'django/db/models/sql/query.py:1:1: D212 [*] Multi-line docstring summary should start at the first line',
            ' '.join([
                'django/db/models/sql/query.py:60:5: ANN202 Missing return type annotation for private function',
                '`get_field_names_from_opts`',
            ]),
            'django/db/models/sql/query.py:60:31: ANN001 Missing type annotation for function argument `opts`',
            'django/db/models/sql/query.py:66:10: COM812 [*] Trailing comma missing',
            ' '.join([
                'django/db/models/sql/query.py:70:5: ANN202 Missing return type annotation for private function',
                '`get_paths_from_expression`',
            ]),
        ],
        [
            'django/db/models/sql/query.py:1:1: D212 [*] Multi-line docstring summary should start at the first line',
        ],
        15,
    )

    assert len(got) == 4


def test_empty_violations() -> None:
    """Test empty violations."""
    got = define_additional(
        [],
        [],
        1,
    )

    assert got == []
