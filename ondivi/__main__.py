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

from contextlib import suppress

from git import Repo

Diff = str
FileName = str


def define_changed_lines(diff: Diff) -> dict[FileName, list[int]]:
    """Поиск измененных строк в файлах.

    :param diff: Diff
    :return: dict[FileName, list[int]]
    """
    res: dict[FileName, list[int]] = {}
    current_file = ''
    for line in diff.splitlines():
        if line.startswith('diff --git'):
            current_file = line.split(' b/')[-1].strip()
            res[current_file] = []
        elif line.startswith('@@'):
            splitted_line = line.split('@@')[1].strip()
            added_lines = splitted_line.split('+')[1]
            start_line = int(
                added_lines.split(',')[0],
            )
            num_lines = 0 if ',' not in added_lines else int(added_lines.split(',')[1]) - 1
            res[current_file].extend(list(range(
                start_line, start_line + num_lines + 1,
            )))
    return res


def filter_out_violations(changed_lines: dict[FileName, list[int]], violations: list[str]) -> list[str]:
    res = []
    for violation in violations:
        with suppress(ValueError, IndexError):
            filename = violation.split(':')[0]
            line = int(violation.split(':')[1])
            if filename not in changed_lines:
                continue
            if line not in changed_lines[filename]:
                continue
        res.append(violation)
    return res


def controller(diff: Diff, violations: list[str]) -> list[str]:
    changed_lines = define_changed_lines(diff)
    return filter_out_violations(changed_lines, violations)


def main() -> None:
    a = 'not empty'
    violations = []
    while a:
        try:
            a = input()
            violations.append(a)
        except EOFError:  # noqa: PERF203
            break
    print('\n'.join(  # noqa: T201
        controller(
            Repo('.').git.diff('--unified=0', 'origin/master..HEAD'),
            violations,
        ),
    ))


if __name__ == '__main__':
    main()
