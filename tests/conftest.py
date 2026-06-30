import pytest
import psycopg2
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_env():
    with patch.dict("os.environ", {
        "OPENAI_API_KEY": "sk-test",
        "COHERE_API_KEY": "co-test",
        "PGHOST": "localhost",
        "PGPORT": "5432",
        "PGUSER": "test",
        "PGDATABASE": "test",
        "PGPASSWORD": "test",
    }):
        yield

@pytest.fixture
def mock_openai():
    with patch("openai.OpenAI") as mock:
        instance = mock.return_value
        instance.embeddings.create.return_value.data = [MagicMock(embedding=[0.1] * 1536)]
        yield mock

@pytest.fixture
def mock_cohere():
    with patch("cohere.Client") as mock:
        instance = mock.return_value
        mock_result = MagicMock()
        mock_result.index = 0
        mock_result.relevance_score = 0.95
        instance.rerank.return_value.results = [mock_result]
        yield mock

@pytest.fixture
def mock_db():
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"content": "Resposta teste", "metadata": {"source": "faq"}, "score": 0.95}
        ]
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_connect
