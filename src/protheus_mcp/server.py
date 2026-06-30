import logging
import os
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from protheus_mcp.search import search_protheus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "protheus-mcp",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

@mcp.tool(
    name="protheus_search",
    description="Search the Protheus FAQ knowledge base for answers about TOTVS Protheus ERP",
)
def protheus_search(question: str) -> str:
    logger.info("protheus_search called with question: %.80s", question)
    try:
        results: list[dict[str, Any]] = search_protheus(question)
    except RuntimeError as e:
        logger.error("Search failed: %s", e)
        return f"Erro ao buscar resultados: {e}"
    except Exception as e:
        logger.error("Unexpected error during search: %s", e)
        return f"Erro inesperado ao buscar resultados. Tente novamente."
    if not results:
        logger.info("No results found for: %.80s", question)
        return f"Nenhum resultado encontrado para: {question}"
    lines: list[str] = []
    for i, r in enumerate(results, start=1):
        score_pct = r["score"] * 100
        lines.append(f"Resultado #{i}")
        lines.append(f"Relevância: {score_pct:.1f}%")
        lines.append(f"Conteúdo: {r['content']}")
        if r.get("metadata"):
            lines.append(f"Metadata: {r['metadata']}")
        lines.append("---")
    logger.info("Returning %d results for: %.80s", len(results), question)
    return "\n".join(lines)

def main() -> None:
    mcp.run(transport="stdio")

def main_sse() -> None:
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8092"))
    logger.info("Starting SSE server on %s:%s", host, port)
    app = mcp.sse_app()
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    uvicorn.run(app, host=host, port=port, log_level="info", proxy_headers=False)

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "sse":
        main_sse()
    else:
        main()
