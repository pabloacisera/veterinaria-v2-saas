from unittest.mock import patch, MagicMock

import numpy as np

from src.infrastructure.rag.embeddings import generate_embedding, get_embedding_model


class TestGenerateEmbedding:
    @patch("src.infrastructure.rag.embeddings.get_embedding_model")
    def test_returns_list_of_floats(self, mock_get_model):
        mock_model = MagicMock()
        mock_model.embed.return_value = iter([np.array([0.1, 0.2, 0.3])])
        mock_get_model.return_value = mock_model

        result = generate_embedding("test text")

        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(v, float) for v in result)
        mock_model.embed.assert_called_once_with(["test text"])

    @patch("src.infrastructure.rag.embeddings.get_embedding_model")
    def test_empty_text(self, mock_get_model):
        mock_model = MagicMock()
        mock_model.embed.return_value = iter([np.array([])])
        mock_get_model.return_value = mock_model

        result = generate_embedding("")
        assert result == []

    @patch("src.infrastructure.rag.embeddings.get_embedding_model")
    def test_384_dims_for_all_minilm(self, mock_get_model):
        mock_model = MagicMock()
        mock_model.embed.return_value = iter([np.array([float(i) for i in range(384)])])
        mock_get_model.return_value = mock_model

        result = generate_embedding("test")
        assert len(result) == 384


class TestGetEmbeddingModel:
    @patch("src.infrastructure.rag.embeddings.TextEmbedding")
    def test_uses_env_var_model_name(self, mock_text_embedding, monkeypatch):
        monkeypatch.setenv("EMBEDDINGS_MODEL", "custom-model")
        get_embedding_model.cache_clear()

        get_embedding_model()

        mock_text_embedding.assert_called_once_with(model_name="custom-model")

    @patch("src.infrastructure.rag.embeddings.TextEmbedding")
    def test_default_model_name(self, mock_text_embedding, monkeypatch):
        monkeypatch.delenv("EMBEDDINGS_MODEL", raising=False)
        get_embedding_model.cache_clear()

        get_embedding_model()

        mock_text_embedding.assert_called_once_with(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
