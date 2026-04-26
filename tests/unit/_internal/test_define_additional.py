# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from ondivi._internal.define_additional import define_additional


def test() -> None:
    got = define_additional(
        [
            "django/db/models/sql/query.py:1:1: D212 [*] Multi-line docstring summary should start at the first line",
            "django/db/models/sql/query.py:60:5: ANN202 Missing return type annotation for private function `get_field_names_from_opts`",
            "django/db/models/sql/query.py:60:31: ANN001 Missing type annotation for function argument `opts`",
            "django/db/models/sql/query.py:66:10: COM812 [*] Trailing comma missing",
            "django/db/models/sql/query.py:70:5: ANN202 Missing return type annotation for private function `get_paths_from_expression`",
        ],
        [
            "django/db/models/sql/query.py:1:1: D212 [*] Multi-line docstring summary should start at the first line",
        ],
        2,
    )

    assert len(got) == 2
    assert got == [
        'django/db/models/sql/query.py:60:5: ANN202 Missing return type annotation for private function `get_field_names_from_opts`', 'django/db/models/sql/query.py:60:5: ANN202 Missing return type annotation for private function `get_field_names_from_opts`'
    ]
