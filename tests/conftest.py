# SPDX-FileCopyrightText: Copyright (c) 2024-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fixtures."""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def localize_violation_path() -> Callable[[str], str]:
    """Localize violation path.

    Violation files contain strings with unix paths, but we need to convert them to windows paths.
    """
    def _localize_violation_path(violation: str) -> str:  # noqa: WPS430
        parts = violation.split(':')
        parts[0] = str(Path(parts[0]))
        return ':'.join(parts)
    return _localize_violation_path
