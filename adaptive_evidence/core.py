"""Persistent, scoped, source-preserving retrieval.

Only Add payloads become memories. Search receives no benchmark labels and
returns original source spans, with source metadata. No synthetic answers or
facts are inserted. All caches are scoped and invalidated after successful Add.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import threading
from collections import Counter, OrderedDict, defaultdict
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

import numpy as np


class Encoder(Protocol):
    identity: str
    def encode(self, texts: list[str], *, query: bool = False) -> np.ndarray: ...


class ConflictError(ValueError):
    pass


TOKEN = re.compile(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]")
STOP = set("a an the is are was were be been being do does did have has had to of in on at for from and or with by it this that these those i you he she they we what which who when where why how can could would should please tell me about".split())
ENUMERATION = re.compile(r"\b(all|both|list|compare|respectively|how many|how much|how long|what were|what are|which events|what activities)\b", re.I)


def tokens(text: str) -> list[str]:
    return [word.casefold() for word in TOKEN.findall(text)]


def content_tokens(text: str) -> set[str]:
    return set(tokens(text)) - STOP


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Config:
    chunk_chars: int = 1000
    overlap_chars: int = 120
    candidate_k: int = 200
    context_chars: int = 24000
    lexical_weight: float = 0.7
    window_radius: int = 1
    cache_users: int = 4

    def __post_init__(self):
        if not (0 <= self.overlap_chars < self.chunk_chars):
            raise ValueError("Invalid chunk overlap")
        if min(self.candidate_k, self.context_chars, self.cache_users) <= 0:
            raise ValueError("Budgets must be positive")
        if self.lexical_weight < 0 or self.window_radius < 0:
            raise ValueError("Weights and window must be non-negative")


def split_spans(text: str, size: int, overlap: int) -> list[tuple[int, int]]:
    """Return exact character offsets; preserve whitespace and every input byte."""
    output = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # Prefer paragraph/sentence boundaries, but guarantee forward progress.
            boundary = max(text.rfind("\n", start + size // 2, end),
                           text.rfind(". ", start + size // 2, end))
            if boundary > start + overlap:
                end = boundary + 1
        output.append((start, end))
        if end == len(text):
            break
        start = end - overlap
    return output


class BM25:
    def __init__(self, texts: list[str]):
        self.count = len(texts)
        self.postings = defaultdict(list)
        lengths = []
        for position, text in enumerate(texts):
            words = tokens(text)
            lengths.append(len(words))
            for word, count in Counter(words).items():
                self.postings[word].append((position, count))
        self.lengths = np.asarray(lengths, dtype=np.float32)
        self.average = float(self.lengths.mean()) if lengths else 1.0

    def scores(self, query: str) -> np.ndarray:
        scores = np.zeros(self.count, dtype=np.float32)
        for term in set(tokens(query)):
            posting = self.postings.get(term, [])
            if not posting:
                continue
            positions, frequencies = np.asarray(posting).T
            idf = math.log(1 + (self.count - len(posting) + .5) / (len(posting) + .5))
            norm = .25 + .75 * self.lengths[positions] / max(self.average, 1.)
            scores[positions] += idf * frequencies * 2.5 / (frequencies + 1.5 * norm)
        return scores


@dataclass
class Index:
    revision: int
    rows: list[dict]
    matrix: np.ndarray
    bm25: BM25
    terms: list[set[str]]
    neighbors: dict[int, list[int]]
    views: object | None = None
    view_lock: object = field(default_factory=threading.RLock)


class MemoryStore:
    def __init__(self, path: str | Path, encoder: Encoder, config: Config | None = None, *, add_indexer=None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.encoder = encoder
        self.add_indexer = add_indexer
        self.config = config or Config()
        self.cache: OrderedDict[str, Index] = OrderedDict()
        self.cache_lock = threading.RLock()
        self.encoder_lock = threading.RLock()
        self.add_locks = [threading.Lock() for _ in range(128)]
        with closing(self.connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS scopes(user_id TEXT PRIMARY KEY,revision INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS requests(
                    user_id TEXT NOT NULL, request_id TEXT NOT NULL, payload_hash TEXT NOT NULL,
                    PRIMARY KEY(user_id,request_id));
                CREATE TABLE IF NOT EXISTS sources(
                    id TEXT PRIMARY KEY,user_id TEXT NOT NULL,request_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,position INTEGER NOT NULL,role TEXT NOT NULL,
                    timestamp INTEGER,content TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS chunks(
                    id TEXT PRIMARY KEY,source_id TEXT NOT NULL REFERENCES sources(id),
                    start INTEGER NOT NULL,end INTEGER NOT NULL,embedding BLOB NOT NULL,
                    index_text TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS source_scope ON sources(user_id);
                CREATE INDEX IF NOT EXISTS chunk_source ON chunks(source_id);
            """)
            identity = digest({"encoder": encoder.identity, "chunk_chars": self.config.chunk_chars,
                               "overlap_chars": self.config.overlap_chars, "schema": 2,
                               "add_indexer": getattr(add_indexer, "identity", None)})
            existing = db.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()
            if existing and existing[0] != identity:
                raise ValueError("Database uses a different model, Add indexer, chunking configuration or schema")
            db.execute("INSERT OR IGNORE INTO metadata VALUES ('identity',?)", (identity,))
            db.commit()

    def connect(self):
        db = sqlite3.connect(self.path, timeout=60)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def add(self, *, user_id: str, request_id: str, session_id: str, messages: list[dict]) -> int:
        if not all(isinstance(x, str) and x for x in (user_id, request_id, session_id)):
            raise ValueError("Missing Add fields")
        # Serialize identical in-process retries before paid model calls. Fixed
        # stripes bound lock memory; database uniqueness also protects processes.
        stripe = int(digest([user_id, request_id])[:8], 16) % len(self.add_locks)
        with self.add_locks[stripe]:
            return self._add(user_id=user_id, request_id=request_id, session_id=session_id, messages=messages)

    def _add(self, *, user_id: str, request_id: str, session_id: str, messages: list[dict]) -> int:
        if not all(isinstance(x, str) and x for x in (user_id, request_id, session_id)) or not messages:
            raise ValueError("Missing Add fields")
        clean = []
        for message in messages:
            if (not isinstance(message.get("role"), str) or not message["role"].strip()
                    or not isinstance(message.get("content"), str) or not message["content"].strip()):
                raise ValueError("Invalid message")
            ts = message.get("timestamp")
            if ts is not None:
                if isinstance(ts, bool) or not isinstance(ts, int):
                    raise ValueError("Timestamp must be integer milliseconds")
                datetime.fromtimestamp(ts / 1000, timezone.utc)
            clean.append({"role": message["role"], "content": message["content"], "timestamp": ts})
        fingerprint = digest({"session_id": session_id, "messages": clean})
        with closing(self.connect()) as db:
            prior = db.execute("SELECT payload_hash FROM requests WHERE user_id=? AND request_id=?",
                               (user_id, request_id)).fetchone()
        if prior:
            if prior[0] != fingerprint:
                raise ConflictError("Request ID has a different payload")
            return 0
        sources, chunks, texts = [], [], []
        for position, message in enumerate(clean):
            source_id = digest([user_id, request_id, position])
            sources.append((source_id, user_id, request_id, session_id, position,
                            message["role"], message["timestamp"], message["content"]))
            for start, end in split_spans(message["content"], self.config.chunk_chars, self.config.overlap_chars):
                chunk_id = digest([source_id, start, end])
                chunks.append((chunk_id, source_id, start, end))
                texts.append(message["content"][start:end])
        index_texts = self.add_indexer.enrich(texts) if self.add_indexer is not None else texts
        if len(index_texts) != len(texts) or any(not isinstance(t, str) or not t for t in index_texts):
            raise ValueError("Invalid Add indexing result")
        if texts:
            with self.encoder_lock:
                matrix = np.asarray(self.encoder.encode(index_texts), dtype=np.float32)
            if matrix.ndim != 2 or len(matrix) != len(texts) or matrix.shape[1] == 0 or not np.isfinite(matrix).all():
                raise ValueError("Invalid embedding matrix")
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            if np.any(norms == 0):
                raise ValueError("Zero embeddings")
            matrix = matrix / norms
        else:
            matrix = []
        with closing(self.connect()) as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                prior = db.execute("SELECT payload_hash FROM requests WHERE user_id=? AND request_id=?",
                                   (user_id, request_id)).fetchone()
                if prior:
                    if prior[0] != fingerprint:
                        raise ConflictError("Request ID has a different payload")
                    return 0
                db.execute("INSERT INTO requests VALUES (?,?,?)", (user_id, request_id, fingerprint))
                db.executemany("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)", sources)
                db.executemany("INSERT INTO chunks VALUES (?,?,?,?,?,?)",
                               [(*chunk, vector.astype(np.float32).tobytes(), text)
                                for chunk, vector, text in zip(chunks, matrix, index_texts)])
                db.execute("INSERT INTO scopes VALUES (?,1) ON CONFLICT(user_id) DO UPDATE SET revision=revision+1", (user_id,))
                db.commit()
            except Exception:
                db.rollback()
                raise
        with self.cache_lock:
            self.cache.pop(user_id, None)
        return len(chunks)

    def index(self, user_id: str) -> Index | None:
        with closing(self.connect()) as db:
            # One read transaction binds the revision to exactly these source rows.
            db.execute("BEGIN")
            scope = db.execute("SELECT revision FROM scopes WHERE user_id=?", (user_id,)).fetchone()
            if not scope:
                return None
            revision = scope[0]
            with self.cache_lock:
                cached = self.cache.get(user_id)
                if cached and cached.revision == revision:
                    self.cache.move_to_end(user_id)
                    return cached
            rows = [dict(row) for row in db.execute("""
                SELECT c.id,c.source_id,c.start,c.end,c.embedding,c.index_text,s.request_id,s.session_id,
                       s.position,s.role,s.timestamp,substr(s.content,c.start+1,c.end-c.start) AS content
                FROM chunks c JOIN sources s ON s.id=c.source_id WHERE s.user_id=?
                ORDER BY s.session_id,s.timestamp,s.request_id,s.position,c.start
            """, (user_id,))]
        if not rows:
            return None
        matrix = np.stack([np.frombuffer(row.pop("embedding"), dtype=np.float32) for row in rows])
        index_texts = [row.pop("index_text") for row in rows]
        groups = defaultdict(list)
        for i, row in enumerate(rows):
            # Only an Add's ordered messages guarantee adjacency. Never infer it
            # from database insertion order or opaque request/session identifiers.
            groups[(row["session_id"], row["request_id"])].append(i)
        neighbors = {}
        for group in groups.values():
            group.sort(key=lambda i: (rows[i]["position"], rows[i]["start"]))
            for position, i in enumerate(group):
                neighbors[i] = group[max(0, position - self.config.window_radius):position + self.config.window_radius + 1]
        texts = [row["content"] for row in rows]
        index = Index(revision, rows, matrix, BM25(index_texts), [content_tokens(t) for t in texts], neighbors)
        with self.cache_lock:
            self.cache[user_id] = index
            self.cache.move_to_end(user_id)
            while len(self.cache) > self.config.cache_users:
                self.cache.popitem(last=False)
        return index

    def ranked(self, index: Index, query: str, options: list[str] | None, mode: str) -> list[int]:
        # Choices are symmetric, low-weight retrieval views. Never insert them
        # as memory or pick one using benchmark labels.
        views = [query] + [query + " " + option for option in (options or [])[:12]]
        with self.encoder_lock:
            vectors = np.asarray(self.encoder.encode(views, query=True), dtype=np.float32)
        if vectors.shape != (len(views), index.matrix.shape[1]) or not np.isfinite(vectors).all():
            raise ValueError("Invalid query embeddings")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        if np.any(norms == 0):
            raise ValueError("Zero query embeddings")
        dense = index.matrix @ (vectors / norms).T
        dense_scores = dense[:, 0]
        order = np.argsort(-dense_scores, kind="stable")
        if mode == "dense":
            return list(map(int, order))
        scores = np.zeros(len(index.rows))
        for view, text in enumerate(views):
            weight = 1.0 if view == 0 else .2 / (len(views) - 1)
            dense_order = np.argsort(-dense[:, view], kind="stable")[:self.config.candidate_k]
            for rank, i in enumerate(dense_order, 1):
                scores[i] += weight / (60 + rank)
            lexical = index.bm25.scores(text)
            lexical_order = np.argsort(-lexical, kind="stable")[:self.config.candidate_k]
            for rank, i in enumerate(lexical_order, 1):
                if lexical[i] > 0:
                    scores[i] += weight * self.config.lexical_weight / (60 + rank)
        from .retrieval_views import MODES, rank_views
        if mode in MODES:
            return rank_views(index, views, vectors / norms, dense_scores, scores,
                              mode, self.config.candidate_k)
        return list(map(int, np.lexsort((-dense_scores, -scores))))

    @staticmethod
    def render(row: dict) -> str:
        metadata = row["role"]
        if row["timestamp"] is not None:
            metadata += " | " + datetime.fromtimestamp(row["timestamp"] / 1000, timezone.utc).isoformat()
        return "[" + metadata + "] " + row["content"]

    def search(self, *, user_id: str, query: str, top_k: int = 100,
               options: list[str] | None = None, mode: str = "hybrid_window") -> list[dict]:
        if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 100:
            raise ValueError("top_k must be between 1 and 100")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Empty query")
        from .retrieval_views import MODES
        if mode not in {"dense", "hybrid", "hybrid_window", "adaptive"} | MODES:
            raise ValueError("Unknown mode")
        index = self.index(user_id)
        if index is None:
            return []
        ranked = self.ranked(index, query, options, mode)
        # Reserve most slots for direct hits. Merge neighbors into a secondary
        # stream so top_k=1 always returns the best direct evidence.
        candidates = list(ranked)
        use_window = mode == "hybrid_window" or (mode == "adaptive" and not ENUMERATION.search(query))
        if use_window:
            effective_k = min(top_k, len(ranked))
            if mode == "adaptive":
                # Estimate how many complete records really fit; a small text
                # budget must not postpone all neighbors until after truncation.
                total = 0
                effective_k = 0
                for i in ranked[:top_k]:
                    length = len(self.render(index.rows[i]))
                    if total + length > self.config.context_chars:
                        break
                    total += length
                    effective_k += 1
            primary_count = max(1, math.ceil(effective_k * .7))
            primary = ranked[:primary_count]
            nearby = []
            for seed in ranked[:min(20, primary_count)]:
                nearby.extend(i for i in index.neighbors[seed] if i != seed)
            candidates = primary + nearby + ranked[primary_count:]
        result, seen, spans = [], set(), defaultdict(list)
        used_chars = 0
        for i in candidates:
            if i in seen:
                continue
            seen.add(i)
            row = index.rows[i]
            # Deduplicate by source span, not text: identical statements at
            # different times can be essential to update/temporal questions.
            if any(start <= row["start"] and end >= row["end"] for start, end in spans[row["source_id"]]):
                continue
            content = self.render(row)
            if used_chars + len(content) > self.config.context_chars:
                continue
            spans[row["source_id"]].append((row["start"], row["end"]))
            item = {"id": row["id"], "content": content, "score": 1.0 / (len(result) + 1)}
            if row["timestamp"] is not None:
                item["created_at"] = datetime.fromtimestamp(row["timestamp"] / 1000, timezone.utc).isoformat()
            result.append(item)
            used_chars += len(content)
            if len(result) == top_k:
                break
        return result

    def purge_user(self, user_id: str):
        """Local administrative retention operation; never exposed publicly."""
        with closing(self.connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM chunks WHERE source_id IN (SELECT id FROM sources WHERE user_id=?)", (user_id,))
            db.execute("DELETE FROM sources WHERE user_id=?", (user_id,))
            db.execute("DELETE FROM requests WHERE user_id=?", (user_id,))
            db.execute("DELETE FROM scopes WHERE user_id=?", (user_id,))
            db.commit()
        with self.cache_lock:
            self.cache.pop(user_id, None)
