# The MIT License (MIT).
#
# Copyright (c) 2024-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Define repo from spec file."""

from pathlib import Path

import yaml
from git import Repo


def define_repo(spec: str, repo_path: Path) -> None:
    """Define repo from spec file."""
    repo = Repo.init(repo_path)
    changes_definition = yaml.safe_load(Path('tests/fixtures/test-repo.yaml').read_text())
    for change in changes_definition['changes']:
        file_path = Path(repo_path / change['path'])
        file_path.parents[0].mkdir(exist_ok=True)
        Path(repo_path / change['path']).write_text(change['content'])
        if change.get('commit'):
            repo.index.add([change['path']])
            repo.index.commit(change['commit']['message'])


if __name__ == '__main__':
    define_repo(
        Path('tests/fixtures/test-repo.yaml').read_text(),
        Path('ondivi-test-repo'),
    )
