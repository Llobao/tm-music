from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="TM Super Agente", version="0.1.0")


POSITIVE_WORDS = {
    "bom",
    "boa",
    "incrível",
    "incrivel",
    "top",
    "amei",
    "melhor",
    "sucesso",
    "excelente",
    "hit",
}

NEGATIVE_WORDS = {
    "ruim",
    "péssimo",
    "pessimo",
    "horrível",
    "horrivel",
    "fracasso",
    "odiei",
    "cancelado",
    "crise",
}


@dataclass
class Mention:
    id: str
    text: str
    source: str
    created_at: datetime
    matched_columns: List[str] = field(default_factory=list)
    sentiment: Literal["positivo", "negativo", "neutro"] = "neutro"


class ColumnCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)


class MentionCreate(BaseModel):
    text: str = Field(min_length=3, max_length=1000)
    source: str = Field(min_length=2, max_length=50, default="web")
    created_at: datetime | None = None


class SuperAgentStore:
    def __init__(self) -> None:
        self._columns: Dict[str, str] = {}
        self._mentions: List[Mention] = []
        self._lock = Lock()

    def add_column(self, keyword: str) -> str:
        normalized = keyword.strip()
        key = normalized.lower()
        with self._lock:
            if key in self._columns:
                raise ValueError("Coluna já cadastrada")
            self._columns[key] = normalized
        return normalized

    def remove_column(self, keyword: str) -> None:
        with self._lock:
            if keyword.lower() not in self._columns:
                raise KeyError("Coluna não encontrada")
            del self._columns[keyword.lower()]

    def list_columns(self) -> List[str]:
        return list(self._columns.values())

    def ingest_mention(self, mention_in: MentionCreate) -> Mention:
        timestamp = mention_in.created_at or datetime.now(timezone.utc)
        text = mention_in.text.strip()
        if not text:
            raise ValueError("Texto vazio")

        matched = [
            value
            for key, value in self._columns.items()
            if key in text.lower()
        ]

        mention = Mention(
            id=str(uuid4()),
            text=text,
            source=mention_in.source.strip(),
            created_at=timestamp,
            matched_columns=matched,
            sentiment=classify_sentiment(text),
        )
        with self._lock:
            self._mentions.append(mention)
        return mention

    def feed(self, keyword: str, limit: int = 50) -> dict:
        display_name = self._columns.get(keyword.lower())
        if display_name is None:
            raise KeyError("Coluna não encontrada")

        selected = [
            m for m in self._mentions if display_name in m.matched_columns
        ]
        selected.sort(key=lambda m: m.created_at, reverse=True)
        selected = selected[:limit]

        sentiment_count = {"positivo": 0, "negativo": 0, "neutro": 0}
        source_count: Dict[str, int] = {}
        for mention in selected:
            sentiment_count[mention.sentiment] += 1
            source_count[mention.source] = source_count.get(mention.source, 0) + 1

        return {
            "column": display_name,
            "volume": len(selected),
            "sentiment": sentiment_count,
            "source_breakdown": source_count,
            "mentions": [asdict(m) for m in selected],
        }


def classify_sentiment(text: str) -> Literal["positivo", "negativo", "neutro"]:
    tokens = {t.strip(".,!?;:\"'()[]{}").lower() for t in text.split()}
    pos = len(tokens & POSITIVE_WORDS)
    neg = len(tokens & NEGATIVE_WORDS)

    if pos > neg:
        return "positivo"
    if neg > pos:
        return "negativo"
    return "neutro"


store = SuperAgentStore()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/columns")
def create_column(payload: ColumnCreate) -> dict:
    try:
        column = store.add_column(payload.name)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"column": column}


@app.get("/columns")
def get_columns() -> dict:
    return {"columns": store.list_columns()}


@app.delete("/columns/{column_name}")
def delete_column(column_name: str) -> dict:
    try:
        store.remove_column(column_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"deleted": column_name}


@app.post("/mentions")
def create_mention(payload: MentionCreate) -> dict:
    mention = store.ingest_mention(payload)
    return {"mention": asdict(mention)}


@app.get("/listening/{column_name}")
def get_listening_feed(column_name: str, limit: int = Query(50, ge=1, le=200)) -> dict:
    try:
        return store.feed(column_name, limit=limit)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
