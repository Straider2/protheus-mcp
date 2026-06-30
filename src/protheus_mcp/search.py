import logging
import os
from typing import Any

import cohere
import openai
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TABLE_NAME = "tbl_faqs_totvs_openai"

def get_embedding(text: str) -> list[float]:
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    try:
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small",
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Failed to generate embedding: {e}") from e

def _get_connection() -> psycopg2.extensions.connection:
    try:
        return psycopg2.connect(
            host=os.environ.get("PGHOST", "localhost"),
            port=int(os.environ.get("PGPORT", 5433)),
            dbname=os.environ["PGDATABASE"],
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
        )
    except KeyError as e:
        raise RuntimeError(f"Missing database environment variable: {e}") from e
    except psycopg2.OperationalError as e:
        raise RuntimeError(
            f"Cannot reach database at {os.environ.get('PGHOST', 'localhost')}:"
            f"{os.environ.get('PGPORT', '5433')} — check host, port, and database name"
        ) from e
    except psycopg2.Error as e:
        raise RuntimeError(f"Database error: {e}") from e

def search_protheus(question: str, top_k: int = 10, rerank_top_n: int = 5) -> list[dict[str, Any]]:
    logger.info("Starting search for: %.80s (top_k=%d)", question, top_k)
    query_vec = get_embedding(question)
    logger.info(
        "Generated embedding (%d dimensions)",
        len(query_vec),
    )
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"SELECT content, metadata, 1 - (embedding <=> %s::vector) AS score "
                f"FROM {TABLE_NAME} ORDER BY score DESC LIMIT %s",
                (query_vec, top_k),
            )
            rows = cur.fetchall()
            logger.info("pgvector returned %d candidates", len(rows))
            if not rows:
                return []
            texts = [r["content"] for r in rows]
            client = cohere.Client(api_key=os.environ["COHERE_API_KEY"])
            reranked = client.rerank(
                query=question,
                documents=texts,
                model="rerank-v3.5",
                top_n=rerank_top_n,
            )
            logger.info("Cohere reranking complete — returning %d results", len(reranked.results))
            results = []
            for r in reranked.results:
                idx = r.index
                row = rows[idx]
                results.append({
                    "content": row["content"],
                    "score": r.relevance_score,
                    "metadata": row["metadata"],
                })
            return results
    except cohere.core.api_error.APIError as e:
        logger.warning("Cohere reranker failed: %s — falling back to pgvector scores", e)
        return [
            {"content": r["content"], "score": r["score"], "metadata": r["metadata"]}
            for r in rows
        ]
    finally:
        conn.close()
        logger.info("Database connection closed")
