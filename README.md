# durable-agentic-quantum

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

Resilient quantum circuit generation

### Tech Stack
Site
- FastHTML

Backend
- FastMCP
- Qiskit
- Temporal
- PostgreSQL

Services
- Google GenAI, gemini-3-flash-preview model

Infra
- Docker

### Local Development
Prepare environment
```shell
uv sync --locked
source .venv/bin/activate
# Acquire API key from https://aistudio.google.com/api-keys
echo "GOOGLE_API_KEY=<key>" >> .env
```

Run application
```shell
docker compose up --build
# Site:        localhost:5001
# Temporal UI: localhost:8233
```

Run unit tests with coverage
```shell
pytest --cov
```

Run checks for formatting, linting, types, etc.
```shell
pre-commit run
```
