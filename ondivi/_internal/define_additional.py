# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import hashlib
from pprint import pformat
from random import Random


def define_additional(linter_output: list[str], filtered_lines: list[str], size: int) -> list[str]:
    not_actual = sorted(list(set(linter_output) - set(filtered_lines)))
    hsh = hashlib.md5(''.join(not_actual).encode('utf-8')).digest()[:4]
    return sorted(Random(hsh).sample(not_actual, k=size))
