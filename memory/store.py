"""
Two-tier memory:
- Vector store (Chroma): semantic recall of past conversations/events
- Structured store (SQLite via SQLAlchemy): durable facts, preferences, task state

Every tenant (user) gets an isolated Chroma collection + a tenant_id column
in the structured tables, so this is multi-tenant/SaaS-ready from the start.
"""
from __future__ import annotations
import chromadb
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()
engine = create_engine("sqlite:///./agent_memory.db")
Session = sessionmaker(bind=engine)


class Fact(Base):
    __tablename__ = "facts"
    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True)
    key = Column(String, index=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(engine)

_chroma_client = chromadb.PersistentClient(path="./chroma_data")


class MemoryStore:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.collection = _chroma_client.get_or_create_collection(f"tenant_{tenant_id}")
        self.session = Session()

    # --- Semantic memory ---
    def remember(self, text: str, doc_id: str, metadata: dict | None = None):
        self.collection.add(documents=[text], ids=[doc_id], metadatas=[metadata or {}])

    def recall(self, query: str, n_results: int = 5) -> list[str]:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results.get("documents", [[]])[0]

    # --- Structured facts (preferences, ongoing task state) ---
    def set_fact(self, key: str, value: str):
        fact = self.session.query(Fact).filter_by(tenant_id=self.tenant_id, key=key).first()
        if fact:
            fact.value = value
            fact.updated_at = datetime.now(timezone.utc)
        else:
            fact = Fact(id=f"{self.tenant_id}:{key}", tenant_id=self.tenant_id, key=key, value=value)
            self.session.add(fact)
        self.session.commit()

    def get_fact(self, key: str) -> str | None:
        fact = self.session.query(Fact).filter_by(tenant_id=self.tenant_id, key=key).first()
        return fact.value if fact else None
