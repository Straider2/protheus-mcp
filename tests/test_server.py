import json
import pytest
from protheus_mcp.search import search_protheus

class TestSearch:
    def test_search_basic(self, mock_env, mock_openai, mock_cohere, mock_db):
        results = search_protheus("Como emitir NF-e?")
        assert len(results) > 0
        assert "content" in results[0]
        assert "score" in results[0]

    def test_search_no_results(self, mock_env, mock_openai, mock_cohere, mock_db):
        mock_db.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = []
        results = search_protheus("pergunta sem resultado")
        assert results == []

    def test_search_empty_question(self, mock_env, mock_openai):
        with pytest.raises(RuntimeError):
            search_protheus("")
