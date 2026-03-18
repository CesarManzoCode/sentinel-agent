from datetime import datetime, timezone
from pathlib import Path

from sentinel.application.memory.consolidation_service import MemoryConsolidationService
from sentinel.application.memory.indexing_service import MemoryIndexingService
from sentinel.application.memory.summarization_service import SummarizationService
from sentinel.config.settings import Settings
from sentinel.domain.common.enums import MemoryType
from sentinel.domain.common.ids import MemoryId
from sentinel.domain.memory.entities import MemoryEntry
from sentinel.infrastructure.memory.embedding_model import LocalEmbeddingModel
from sentinel.infrastructure.memory.retrievers.bm25_retriever import BM25Retriever
from sentinel.infrastructure.memory.retrievers.fusion_retriever import FusionRetriever
from sentinel.infrastructure.memory.retrievers.vector_retriever import VectorRetriever
from sentinel.infrastructure.memory.summarizers.conversation_summarizer import ConversationSummarizer
from sentinel.infrastructure.persistence.db import DatabaseManager
from sentinel.infrastructure.persistence.repositories.memory_repository import SQLiteMemoryRepository
from sentinel.infrastructure.persistence.vector.embedding_cache import EmbeddingCache
from sentinel.infrastructure.persistence.vector.hnsw_index import HNSWIndexStore


def test_memory_roundtrip_with_lexical_and_vector_components(tmp_path: Path) -> None:
    db = DatabaseManager(tmp_path / "sentinel.db")
    db.initialize()
    repo = SQLiteMemoryRepository(db)
    cache = EmbeddingCache(db)
    embeddings = LocalEmbeddingModel(64, cache=cache)
    index = HNSWIndexStore(tmp_path / "vector", 64)
    indexing = MemoryIndexingService(repo, embeddings)

    now = datetime.now(timezone.utc)
    memory = MemoryEntry(
        memory_id=MemoryId.new(),
        memory_type=MemoryType.EPISODIC,
        text="The package install failed because the pacman database lock was held.",
        created_at=now,
        updated_at=now,
        salience=0.8,
    )
    repo.save(memory)
    vector = indexing.index(memory)
    index.add(memory.memory_id.value, vector)

    lexical = BM25Retriever(repo)
    semantic = VectorRetriever(repo, embeddings, index)
    fusion = FusionRetriever(lexical=lexical, semantic=semantic)

    result = fusion.retrieve("pacman database lock", 5)

    assert result.items
    assert result.items[0].memory.text.startswith("The package install failed")
