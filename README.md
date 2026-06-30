# Protheus Chat MCP Server

MCP (Model Context Protocol) server that exposes a knowledge base search tool
for **TOTVS Protheus ERP**. Uses **pgvector** for vector similarity search,
**OpenAI** (`text-embedding-3-small`) for question embeddings, and
**Cohere** (`rerank-v3.5`) for result reranking.

Full documentation in the repository.

## Quick Start

```bash
git clone https://github.com/Straider2/protheus-mcp.git
cd protheus-mcp
cp .env.example .env
# edit .env with your credentials
uv pip install -e .
mcp-server-protheus
```

## Remote Access (SSE)

```json
{
  "mcpServers": {
    "protheus": {
      "url": "https://your-host/sse"
    }
  }
}
```
