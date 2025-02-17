<!---
The MIT License (MIT).

Copyright (c) 2024-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
-->
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `Dockerfile` for development (#145)

### Changed

- Replace `Makefile` -> `Taskfile.yml` (#137)
- Update license year to 2025 (#143)
- Separate lint requirements, use ruff (#143)
- Updated dev dependencies
- Replace zip archive for integration test to create repo from `yaml` file (#174)

### Removed

- isort

## [0.6.0] - 2024-10-05

### Added

- Reading violations from file. `--fromfile` flag (#109)
- Handle "revision not found" (#125)

### Changed

- `--help` output (#43)

## [0.5.0] - 2024-06-21

### Added

- Lint via pylint (#39)
- Handle exception (#42)
- `click` for CLI (#45)
- Show only violations in output. `--only-violations` flag (#48)

## [0.4.1] - 2024-06-14

### Changed

- Availabe python version (#36)

### Fixed

- Test custom violation format (#34)

## [0.4.0] - 2024-06-13

### Added

- Test `mypy` violations
- Tests for `python3.13`
- `--format` cli parameter for custom error format

## [0.3.1] - 2024-05-28

### Added

- Test exit code without violations (#19)

### Fixed

- Out with info messages (#20)

## [0.3.0] - 2024-05-28

### Added

- Test for `ruff` violations

### Changed

- Extend `gitpython` version (#14)
- Simplify script (#15)
- Fail on exist violations (#17)

## [0.2.1] - 2024-05-27

### Fixed

- Release workflow

## [0.2.0] - 2024-05-27

### Added

- Deltaver (#9)
- Mutation coverage workflow (#10)
- `baseline` cli parameter (#11)

## [0.1.0] - 2024-05-16

### Added

- Renovate (#1)

### Changed

- Lint via ruff, mypy (#4)

## [0.0.1a6] - 2024-05-16

## [0.0.1a5] - 2024-05-16

### Removed

- Old test

## [0.0.1a4] - 2024-05-16

### Fixed

- Tests path

## [0.0.1a3] - 2024-05-16

### Added

- Initial version

[unreleased]: https://github.com/blablatdinov/ondivi/compare/0.6.0...HEAD
[0.6.0]: https://github.com/blablatdinov/ondivi/compare/0.5.0...0.6.0
[0.5.0]: https://github.com/blablatdinov/ondivi/compare/0.4.1...0.5.0
[0.4.1]: https://github.com/blablatdinov/ondivi/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/blablatdinov/ondivi/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/blablatdinov/ondivi/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/blablatdinov/ondivi/compare/0.2.1...0.3.0
[0.2.1]: https://github.com/blablatdinov/ondivi/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/blablatdinov/ondivi/compare/0.1.0...0.2.0
[0.1.0]: https://github.com/blablatdinov/ondivi/compare/0.0.1a6...0.1.0
[0.0.1a6]: https://github.com/blablatdinov/ondivi/compare/0.0.1a5...0.0.1a6
[0.0.1a5]: https://github.com/blablatdinov/ondivi/compare/0.0.1a4...0.0.1a5
[0.0.1a4]: https://github.com/blablatdinov/ondivi/compare/0.0.1a3...0.0.1a4
[0.0.1a3]: https://github.com/blablatdinov/ondivi/releases/tag/0.0.1a3
