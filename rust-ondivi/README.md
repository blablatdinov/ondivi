# ondivi (Rust)

**Only diff violations** — фильтрует вывод линтера только по изменённым строкам в git-репозитории.

Это Rust-переписывание оригинального Python-инструмента [ondivi](https://github.com/blablatdinov/ondivi). Пока находится в отдельной директории для параллельной разработки; после стабилизации заменит Python-версию.

## Установка

```bash
cargo install ondivi
```

Или из исходников:

```bash
cd rust-ondivi
cargo install --path .
```

Prebuilt binaries для Linux/macOS/Windows доступны в [GitHub Releases](../../releases).

## Использование

```bash
flake8 script.py | ondivi
ruff check file.py --output-format=concise | ondivi
mypy script.py | ondivi --baseline main
```

Опции:

| Флаг | Описание | По умолчанию |
|------|----------|--------------|
| `--baseline <REF>` | Коммит или ветка с legacy-кодом | `master` |
| `--fromfile <PATH>` | Читать нарушения из файла вместо stdin | — |
| `--format <TPL>` | Шаблон парсинга сообщений линтера | `{filename}:{line_num:d}{other}` |
| `--only-violations` | Показывать только violations (без info-сообщений) | off |
| `--random-additional <N>` | *(пока не реализовано)* | — |

Коды выхода:
- `0` — нарушений на изменённых строках нет
- `1` — найдены нарушения / ошибка (не найден файл, ревизия)
- `2` — некорректные аргументы CLI

## Отличия от Python-версии

- `--random-additional` пока не реализован (детерминированный random требует реимплементации Mersenne Twister)
- Исключительные ситуации печатаются иначе (нет Python traceback)
- Остальное поведение идентично

## Разработка

```bash
cargo test
cargo build
cargo clippy
```
