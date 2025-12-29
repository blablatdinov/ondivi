# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
