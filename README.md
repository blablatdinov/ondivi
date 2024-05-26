# Ondivi (Only diff violations)

[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![Lines of code](https://tokei.rs/b1/github/blablatdinov/ondivi)](https://github.com/XAMPPRocky/tokei)
[![Hits-of-Code](https://hitsofcode.com/github/blablatdinov/ondivi)](https://hitsofcode.com/github/blablatdinov/quranbot-aiogram/view)

This is a simple Python script designed to filter coding violations (likely identified by a static analyzer) for only the lines that have been changed in a Git repository.

## Prerequisites:

- Python 3.9 or higher
- Git

## Installation

```bash
pip install ondivi
```

## Usage

Ensure you are in the root directory of your Git repository.

Run the script:

```bash
flake8 script.py | ondivi
```

## How it Works

The script parses the Git diff output to identify the changed lines in each file.

It then filters the given coding violations to include only those violations that correspond to the changed lines.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
