# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import hashlib
from random import Random

from ondivi._internal.exceptions import InvalidSizeError
from ondivi._internal.ondivi_types import ValidAdditionalSize


def valid_size(size: int) -> ValidAdditionalSize:
    if size < 1:
        raise InvalidSizeError
    return size


def define_additional(linter_output: list[str], filtered_lines: list[str], size: ValidAdditionalSize) -> list[str]:
    if not linter_output:
        return []
    not_actual = sorted(set(linter_output) - set(filtered_lines))
    size = min(size, len(not_actual))
    hsh = hashlib.md5(  # noqa: S324
        ''.join(not_actual).encode('utf-8'),
    ).digest()[:4]
    return sorted(Random(hsh).sample(not_actual, k=size))  # noqa: S311
