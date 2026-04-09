# xaue-mcp

A minimal Python MCP server with one callable tool method.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run Server

```bash
python main.py
```

or:

```bash
xaue-mcp
```

## Callable Method

This project exposes one MCP tool:

- `hello(name: str = "MCP") -> str`

Internally it calls:

- `build_greeting(name: str) -> str`

You can also call it directly in Python:

```bash
python -c "from main import build_greeting; print(build_greeting('World'))"
```
