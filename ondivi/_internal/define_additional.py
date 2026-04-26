# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from random import Random
import hashlib


def define_additional(linter_output: list[str], filtered_lines: list[str], size: int) -> list[str]:
    not_actual = list(set(linter_output) - set(filtered_lines))
    hsh = hashlib.md5(''.join(sorted(not_actual)).encode('utf-8')).digest()[:4]
    print('!!!', hsh)
    return sorted(Random(hsh).choices(not_actual, k=size))
