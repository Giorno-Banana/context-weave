"""Synchronous AML contract with private validation errors and fail-closed auth."""
from __future__ import annotations

import hmac
import logging
import os
import time
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .core import Config, ConflictError, MemoryStore
from .remote_encoder import EmbeddingError, encoder_from_env
from .add_indexer import AddIndexerError, add_indexer_from_env


class Message(BaseModel):
    role: str = Field(min_length=1)
    content: str = Field(min_length=1)
    timestamp: int | None = Field(default=None, strict=True)


class Add(BaseModel):
    request_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    messages: list[Message] = Field(min_length=1)


class Search(BaseModel):
    # Forbid accidental label/evidence fields in the public search contract.
    model_config = ConfigDict(extra="forbid")
    user_id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    options: list[str] | None = None
    top_k: int = Field(ge=1, le=100, strict=True)


@lru_cache(maxsize=1)
def get_store():
    encoder = encoder_from_env()
    add_indexer = None
    try:
        add_indexer = add_indexer_from_env()
        return MemoryStore(os.getenv("AE_DATABASE", "data/cycle2-v4/memory.sqlite3"),
                           encoder, Config(context_chars=int(os.getenv("AE_CONTEXT_CHARS", "24000"))),
                           add_indexer=add_indexer)
    except Exception:
        if hasattr(encoder, "close"):
            encoder.close()
        if add_indexer is not None:
            add_indexer.close()
        raise


@lru_cache(maxsize=1)
def get_planner():
    from .planner import OpenAIPlanner
    return OpenAIPlanner(os.environ["OPENAI_API_KEY"], max_calls=int(os.getenv("AE_PLANNER_MAX_CALLS", "2000")))


def authenticate(authorization: str | None = Header(default=None), x_api_key: str | None = Header(default=None)):
    expected = os.getenv("MEMORY_API_KEY", "")
    if not expected:
        if os.getenv("AE_LOCAL_NO_AUTH") == "1":
            return
        raise HTTPException(503, "Memory service key is not configured")
    provided = x_api_key
    if not provided and authorization:
        scheme, _, credential = authorization.partition(" ")
        if scheme.lower() in {"bearer", "token"}:
            provided = credential
    if not provided or not hmac.compare_digest(provided.encode(), expected.encode()):
        raise HTTPException(401, "Invalid service key")


@asynccontextmanager
async def lifespan(app):
    if not os.getenv("MEMORY_API_KEY") and os.getenv("AE_LOCAL_NO_AUTH") != "1":
        raise RuntimeError("MEMORY_API_KEY is required before starting the service")
    store = get_store()
    planner = None
    try:
        if os.getenv("AE_PLANNER") == "1":
            planner = get_planner()
        yield
    finally:
        if hasattr(store.encoder, "close"):
            store.encoder.close()
        if store.add_indexer is not None:
            store.add_indexer.close()
        if planner is not None:
            planner.client.close()
        get_store.cache_clear()
        get_planner.cache_clear()


LOG = logging.getLogger("adaptive_evidence")
LOG.setLevel(logging.INFO)
LOG.propagate = False
if not LOG.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    LOG.addHandler(handler)

app = FastAPI(title="Context Weave", version="0.3.1", lifespan=lifespan)


@app.middleware("http")
async def request_timing(request, call_next):
    started = time.monotonic()
    response = await call_next(request)
    if request.url.path in {"/add", "/search"}:
        LOG.info("api_request path=%s status=%s seconds=%.2f", request.url.path,
                 response.status_code, time.monotonic() - started)
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(status_code=422, content={"detail": "Invalid request schema"})


@app.exception_handler(EmbeddingError)
async def embedding_error(request, exc):
    LOG.warning("embedding_failure reason=%s", str(exc))
    return JSONResponse(status_code=503, content={"detail": str(exc)}, headers={"Retry-After": "5"})


@app.exception_handler(AddIndexerError)
async def add_indexer_error(request, exc):
    LOG.warning("add_failure reason=%s", str(exc))
    return JSONResponse(status_code=503, content={"detail": str(exc)}, headers={"Retry-After": "5"})


@app.get("/health")
def health(store: MemoryStore = Depends(get_store)):
    return {"status": "ok", "version": "0.3.1",
            "embedding": getattr(store.encoder, "model", "local-or-test"),
            "llm": "gpt-4o-mini" if store.add_indexer is not None or os.getenv("AE_PLANNER") == "1" else "none",
            "add_llm": getattr(store.add_indexer, "model", "none"),
            "llm_provider": "openrouter" if store.add_indexer is not None else "none"}


@app.post("/add", dependencies=[Depends(authenticate)])
def add(payload: Add, store: MemoryStore = Depends(get_store)):
    try:
        store.add(**payload.model_dump())
    except ConflictError:
        raise HTTPException(409, "Request ID conflicts with an existing write")
    except (ValueError, OverflowError, OSError):
        raise HTTPException(422, "Invalid memory data")
    return {"success": True, "request_id": payload.request_id,
            "user_id": payload.user_id, "session_id": payload.session_id}


@app.post("/search", dependencies=[Depends(authenticate)])
def search(payload: Search, store: MemoryStore = Depends(get_store)):
    from .planner import PlannedMemory, PlannerError
    try:
        if os.getenv("AE_PLANNER") == "1":
            return {"data": PlannedMemory(store, get_planner()).search(**payload.model_dump())}
        return {"data": store.search(**payload.model_dump(), mode=os.getenv("AE_MODE", "hybrid_window"))}
    except (PlannerError, KeyError):
        raise HTTPException(503, "Planner unavailable; evaluation profile has not been changed")
    except ValueError:
        raise HTTPException(422, "Invalid search data")
