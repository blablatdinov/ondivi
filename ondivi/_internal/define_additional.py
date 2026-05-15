# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import hashlib
from pprint import pformat
from random import Random


def define_additional(linter_output: list[str], filtered_lines: list[str], size: int) -> list[str]:
    not_actual = list(set(linter_output) - set(filtered_lines))
    hsh = hashlib.md5(''.join(sorted(not_actual)).encode('utf-8')).digest()[:4]
    print('linter_output =', pformat(linter_output, width=200))
    print('not actual =', pformat(not_actual, width=200))
    print('hash =', hsh)
    print('random violations =', pformat(sorted(Random(hsh).sample(not_actual, k=size)), width=200))
    return sorted(Random(hsh).sample(not_actual, k=size))
