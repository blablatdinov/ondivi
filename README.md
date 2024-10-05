# Ondivi (Only diff violations)

[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![PyPI version](https://badge.fury.io/py/ondivi.svg)](https://badge.fury.io/py/ondivi)
![CI status](https://github.com/blablatdinov/ondivi/actions/workflows/pr-check.yml/badge.svg?branch=master)
[![Lines of code](https://tokei.rs/b1/github/blablatdinov/ondivi)](https://github.com/XAMPPRocky/tokei_rs)
[![Hits-of-Code](https://hitsofcode.com/github/blablatdinov/ondivi)](https://hitsofcode.com/github/blablatdinov/quranbot-aiogram/view)

This is a simple Python script designed to filter coding violations (likely identified by a static analyzer) for only the lines that have been changed in a Git repository.

This tool works with any linter or static code analyzer, including but not limited to:

- [Flake8](https://github.com/PyCQA/flake8)
- [Ruff](https://github.com/astral-sh/ruff)
- [Pylint](https://github.com/pylint-dev/pylint)
- [Mypy](https://github.com/python/mypy)
- [Eslint](https://github.com/eslint/eslint)
- [Rubocop](https://github.com/rubocop/rubocop)
- [Stylelint](https://github.com/stylelint/stylelint)

## Prerequisites:

- [Python](https://python.org) 3.9 or higher
- [Git](https://git-scm.com/)

## Installation

```bash
pip install ondivi
```

## Usage

Ensure you are in the root directory of your Git repository.

Run the script:

```bash
flake8 script.py | ondivi
# with ruff:
ruff check file.py --output-format=concise | ondivi
```

or:

```bash
flake8 script.py > violations.txt
ondivi --fromfile=violations.txt
```

```
$ ondivi --help
Usage: ondivi [OPTIONS]

  Ondivi (Only diff violations).

  Python script filtering coding violations, identified by static analysis,
  only for changed lines in a Git repo. Usage example:

  flake8 script.py | ondivi

Options:
  --baseline TEXT    Commit or branch which will contain legacy code. Program
                     filter out violations on baseline (default: "master")
  --fromfile TEXT    Path to file with violations. Expected "utf-8" encoding
  --format TEXT      Template for parsing linter messages. The template should
                     include the following named parts:

                     {filename}   The name of the file with the error/warning
                     {line_num}   The line number with the error/warning
                     (integer)

                     Example usage:

                     --format "{filename}:{line_num:d}{other}"

                     In this example, the linter message

                     "src/app_types/listable.py:23:1: UP035 Import from
                     collections.abc instead: Sequence"

                     will be recognized and parsed into the following
                     components:

                      - filename: "src/app_types/listable.py"
                      - line_num: 23
                      - other: :1: "UP035 Import from collections.abc instead:
                      Sequence"

                     Ensure that the template matches the format of the
                     messages generated by your linter.
                     (default: "{filename}:{line_num:d}{other}")
  --only-violations  Show only violations
  --help             Show this message and exit.
```

## How it works

The script parses the Git diff output to identify the changed lines in each file.

It then filters the given coding violations to include only those violations that correspond to the changed lines.

[flakeheaven](https://github.com/flakeheaven/flakeheaven) and [flakehell](https://github.com/flakehell/flakehell)
are not supported because they rely on internal flake8 API, which can lead to compatibility issues as flake8
evolves. In contrast, ondivi uses only the text output of violations and the state of Git repository, making
it more robust and easier to maintain.

Flake8 on file:

```bash
$ flake8 file.py
file.py:3:1: E302 expected 2 blank lines, found 1
file.py:9:1: E302 expected 2 blank lines, found 1
file.py:10:121: E501 line too long (123 > 120 characters)
file.py:14:1: E305 expected 2 blank lines after class or function definition, found 1
```

Example of changes:

```diff
 from dataclasses import dataclass

 @dataclass
 class User(object):

     name: str
     age: int

 def greet(user: User):
     print('Long string in initial commit ################################################################################')
     print(f'Hello, {user.name}!')
+    print('Long string in new commit ################################################################################')

 if __name__ == '__main__':
     greet(User(345, 23))
+    greet(User('Bob', '23'))
```

By git diff we see, that two new lines were appended (12 and 16):

Ondivi filters out violations and shows only one for line 12:

```bash
$ flake8 script.py | ondivi
file.py:12:80: E501 line too long (119 > 79 characters)
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
