import logging
import os
import time
from functools import lru_cache

import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, engine
from models import Book as BookModel
from recommender_service import recommend, books as ml_books

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter

ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
ENABLE_GZIP = os.getenv("ENABLE_GZIP", "true").lower() == "true"
ENABLE_SECURITY_HEADERS = os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
RATE_LIMIT_RECOMMEND = os.getenv("RATE_LIMIT_RECOMMEND", "20/minute")


def _db_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    if ENABLE_SECURITY_HEADERS:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s %d %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

if ENABLE_GZIP:
    app.add_middleware(GZipMiddleware, minimum_size=1000)

DEFAULT_GENRES = {
    "Art", "Biography", "Business", "Children's", "Christian", "Classics",
    "Comics", "Cookbooks", "Ebooks", "Fantasy", "Fiction", "Graphic Novels",
    "Historical Fiction", "History", "Horror", "Memoir", "Music", "Mystery",
    "Nonfiction", "Poetry", "Psychology", "Romance", "Science",
    "Science Fiction", "Self Help", "Sports", "Thriller", "Travel",
    "Young Adult",
}

MATH_GENRES = [
    "Mathematics", "Physics", "Computer Science",
    "Programming", "Engineering", "Logic", "Calculus",
    "Statistics", "Computation", "Computers", "Popular Science",
]


def clean_genres(raw: str) -> str:
    if not raw:
        return ""
    seen = set()
    result = []
    for g in raw.split(","):
        g = g.strip()
        if g and g not in DEFAULT_GENRES and g not in seen:
            seen.add(g)
            result.append(g)
    return ", ".join(result)


def to_native(val):
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, np.bool_):
        return bool(val)
    if isinstance(val, np.ndarray):
        return val.tolist()
    return val


def book_to_dict(row):
    return {
        "bookId": to_native(row["bookId"]),
        "title": str(row["title"]),
        "author": str(row["author"]),
        "genres": clean_genres(str(row.get("genres", ""))),
        "description": str(row.get("description", "")),
    }


def book_model_to_dict(book: BookModel) -> dict:
    return {
        "bookId": book.id,
        "title": book.title,
        "author": book.author,
        "genres": clean_genres(book.genres),
        "description": book.description,
    }


class RecommendRequest(BaseModel):
    title: str


@app.get("/books")
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_books(request: Request, q: str = "", db: Session = Depends(get_db)):
    use_db = _db_available()
    if use_db:
        if q:
            rows = (
                db.query(BookModel)
                .filter(BookModel.title.ilike(f"%{q}%"))
                .limit(20)
                .all()
            )
        else:
            rows = db.query(BookModel).limit(50).all()
        return [book_model_to_dict(b) for b in rows]
    elif ml_books is not None:
        if q:
            filtered = ml_books[ml_books["title"].str.contains(q, case=False, na=False, regex=False)]
            rows = filtered.head(20)
        else:
            rows = ml_books.head(50)
        return [book_to_dict(r) for _, r in rows.iterrows()]
    else:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@app.get("/books/popular")
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_popular_books(request: Request, limit: int = Query(default=6, ge=1, le=50), db: Session = Depends(get_db)):
    use_db = _db_available()
    if use_db:
        rows = db.query(BookModel).limit(limit).all()
        return [book_model_to_dict(b) for b in rows]
    elif ml_books is not None:
        rows = ml_books.head(limit)
        return [book_to_dict(r) for _, r in rows.iterrows()]
    else:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@app.get("/genres")
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_genres(request: Request):
    return sorted(MATH_GENRES)


@app.get("/books/{book_id}")
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_book(request: Request, book_id: int, db: Session = Depends(get_db)):
    use_db = _db_available()
    if use_db:
        book = db.query(BookModel).filter(BookModel.id == book_id).first()
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
        return book_model_to_dict(book)
    elif ml_books is not None:
        book = ml_books[ml_books["bookId"] == book_id]
        if book.empty:
            raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
        return book_to_dict(book.iloc[0])
    else:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")


@lru_cache(maxsize=2048)
def _cached_recommend(title: str, top_n: int = 5):
    return recommend(title, top_n=top_n)


@app.post("/recommend")
@limiter.limit(RATE_LIMIT_RECOMMEND)
def post_recommend(request: Request, req: RecommendRequest):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Title must not be empty")
    result = _cached_recommend(req.title.strip())
    if not result:
        raise HTTPException(status_code=404, detail=f"Book '{req.title}' not found")
    return {"recommendations": [
        {k: to_native(v) for k, v in rec.items()} for rec in result
    ]}


_featured_cache: dict = {}
_FEATURED_TTL = 300


@app.get("/recommend/featured")
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_featured_recommendation(request: Request):
    now = time.time()
    if _featured_cache.get("data") and now - _featured_cache.get("ts", 0) < _FEATURED_TTL:
        return _featured_cache["data"]

    if ml_books is None or len(ml_books) == 0:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")

    sample = ml_books.sample(1).iloc[0]
    recs = recommend(sample["title"], top_n=6)
    data = {
        "book": {
            "bookId": to_native(sample["bookId"]),
            "title": str(sample["title"]),
            "author": str(sample["author"]),
        },
        "recommendations": [
            {k: to_native(v) for k, v in rec.items()} for rec in recs
        ],
    }
    _featured_cache["data"] = data
    _featured_cache["ts"] = now
    return data


@app.get("/health")
@limiter.limit(RATE_LIMIT_DEFAULT)
def health_check(request: Request):
    model_loaded = ml_books is not None and len(ml_books) > 0
    db_ok = _db_available()
    return {
        "status": "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "database_connected": db_ok,
        "total_books": len(ml_books) if ml_books is not None else 0,
    }
