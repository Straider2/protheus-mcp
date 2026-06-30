# Protheus Chat MCP Server

MCP (Model Context Protocol) server that exposes a knowledge base search tool
for **TOTVS Protheus ERP**. Uses **pgvector** for vector similarity search,
**OpenAI** (`text-embedding-3-small`) for question embeddings, and
**Cohere** (`rerank-v3.5`) for result reranking.

## Quick Start

```bash
git clone https://github.com/Straider2/protheus-mcp.git
cd protheus-mcp
cp .env.example .env
# edit .env with your credentials
uv pip install -e .
mcp-server-protheus
```

Or run remotely via SSE:

```json
{
  "mcpServers": {
    "protheus": {
      "url": "https://mcp-protheus.yourdomain.com/sse"
    }
  }
}
```

## Configuration

| Variable | Default | Required |
|---|---|---|
| `PGHOST` | `localhost` | Database host |
| `PGPORT` | `5433` | Database port |
| `PGUSER` | — | Database user |
| `PGDATABASE` | — | Database name |
| `PGPASSWORD` | — | Database password |
| `OPENAI_API_KEY` | — | OpenAI API key (embeddings) |
| `COHERE_API_KEY` | — | Cohere API key (reranking) |

Copy `.env.example` to `.env` and fill in your values.

## Installation

### Local (stdio)

```bash
uv pip install -e .
mcp-server-protheus
```

Available commands:
- `mcp-server-protheus` — stdio MCP server (Claude Desktop, Cursor)
- `mcp-server-protheus-sse` — SSE/HTTP server (remote access)
- `protheus-mcp` — alias for stdio

### Docker (SSE)

```bash
docker compose -f docker-compose.yml up -d protheus-mcp-sse
```

The server listens on `http://localhost:8092/sse`.

## Usage

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "protheus": {
      "command": "uv",
      "args": ["run", "mcp-server-protheus"]
    }
  }
}
```

### Remote via SSE URL

```json
{
  "mcpServers": {
    "protheus": {
      "url": "https://mcp-protheus.yourdomain.com/sse"
    }
  }
}
```

### Available Tool

**`protheus_search(question: str)`** — Search the Protheus FAQ knowledge base.

## Architecture

```
User Question → OpenAI Embedding → pgvector Cosine Search → Cohere Rerank → Results
```

The server connects **read-only** to PostgreSQL/pgvector.

## Testing

```bash
uv run pytest tests/ -v
```

All tests use mocked connections — no real credentials needed.

## Project Structure

```
protheus-mcp/
├── .env.example
├── pyproject.toml
├── README.md
├── src/protheus_mcp/
│   ├── __init__.py
│   ├── search.py      # pgvector search + Cohere rerank
│   └── server.py      # MCP server (stdio + SSE)
└── tests/
    ├── conftest.py
    └── test_server.py
```

## License

MIT
