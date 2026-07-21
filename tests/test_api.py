import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_get_books():
    resp = client.get("/books")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_books_search():
    resp = client.get("/books?q=Harry Potter")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0
    assert any("Harry Potter" in b["title"] for b in data)


def test_get_book_detail():
    resp = client.get("/books/1")
    assert resp.status_code == 200
    data = resp.json()
    assert "title" in data
    assert "author" in data


def test_get_book_not_found():
    resp = client.get("/books/99999")
    assert resp.status_code == 404


def test_get_genres():
    resp = client.get("/genres")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert "Mathematics" in data


def test_post_recommend():
    resp = client.post("/recommend", json={"title": "1984"})
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0


def test_post_recommend_not_found():
    resp = client.post("/recommend", json={"title": "Buku Tidak Ada XYZ"})
    assert resp.status_code == 404


def test_post_recommend_empty_title():
    resp = client.post("/recommend", json={"title": "   "})
    assert resp.status_code == 400


def test_get_popular_books():
    resp = client.get("/books/popular?limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3


def test_get_featured_recommendation():
    resp = client.get("/recommend/featured")
    assert resp.status_code == 200
    data = resp.json()
    assert "book" in data
    assert "recommendations" in data


def test_security_headers():
    resp = client.get("/health")
    assert resp.headers.get("x-content-type-options") == "nosniff"
    assert resp.headers.get("x-frame-options") == "DENY"
    assert resp.headers.get("x-xss-protection") == "1; mode=block"
    assert resp.headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in resp.headers.get("content-security-policy", "")
    assert "max-age=31536000" in resp.headers.get("strict-transport-security", "")


def test_health_check_model_loaded():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_loaded"] is True
    assert data["total_books"] > 0
