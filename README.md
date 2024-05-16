# Ondivi (Only diff violations)

This is a simple Python script designed to filter coding violations (likely identified by a static analyzer) for only the lines that have been changed in a Git repository.

## Prerequisites:

- Python 3.9 or higher
- GitPython library (pip install GitPython)

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
