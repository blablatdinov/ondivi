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

import subprocess
from pathlib import Path

from ondivi.__main__ import define_changed_lines


def test():
    ps = subprocess.Popen(('echo', 'hello'), stdout=subprocess.PIPE)
    got = subprocess.check_output(('poetry', 'run', 'ondivi'), stdin=ps.stdout).decode().strip()
    ps.wait()

    assert got == 'hello'


def test_define_changed_files():
    got = define_changed_lines(
        Path('tests/fixtures/diff.txt').read_text(),
    )

    assert got == {
        'src/app_types/listable.py': [23, 29, 33, 36, 37, 44, 47, 49],
        'src/srv/ayats/ayat_by_id_answer.py': [36, 58],
        'src/srv/ayats/ayat_by_sura_ayat_num_answer.py': [38, 59],
        'src/srv/ayats/ayats_by_text_query.py': [23, 33, 34, 47, 62, 63, 64, 65, 66],
        'src/srv/ayats/change_favorite_ayat_answer.py': [55, 77, 78, 79, 80, 81, 82, 84],
        'src/srv/ayats/favorite_ayats.py': [33, 60],
        'src/srv/ayats/favorite_ayats_after_remove.py': [23, 34, 48, 67, 69],
        'src/srv/ayats/favorites/user_favorite_ayats.py': [32, 60],
        'src/srv/ayats/neighbor_ayats.py': [33, 137, 154, 197, 198, 199, 213, 214, 215],
        'src/srv/ayats/pg_ayat.py': [28, 36, *range(44, 91), 100],
        'src/tests/fixtures/2_282_ayat_rendered.txt': [1, 2, 3, 4, 5, 6],
        'src/tests/fixtures/2_282_ayat_without_transliteration.txt': [1, 2, 3, 4],
        'src/tests/it/srv/ayats/test_pg_ayat.py': [24, 30, 31, 32, 33, 34, *range(74, 98)],
    }
