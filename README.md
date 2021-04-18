# telegram-proc-control
Control a process from Telegram

## Install
Requires: [python-poetry](https://python-poetry.org/)

```bash
poetry install
```

## Usage
```bash
poetry run python bot.py "$TOKEN" "$COMMAND"
```

For example:
```bash
poetry run python bot.py "$TOKEN" "sleep 10"
```
