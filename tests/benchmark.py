import sys
import os
import time
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi.testclient import TestClient
from app import app, _cached_recommend

client = TestClient(app)

ENDPOINTS = [
    ("GET", "/books"),
    ("GET", "/books?q=math"),
    ("GET", "/books/1"),
    ("GET", "/books/popular?limit=6"),
    ("GET", "/genres"),
    ("GET", "/recommend/featured"),
    ("GET", "/health"),
]

SAMPLE_TITLES = [
    "1984", "Harry Potter and the Sorcerer's Stone", "The Hobbit",
    "To Kill a Mockingbird", "The Great Gatsby", "Pride and Prejudice",
    "The Da Vinci Code", "Lord of the Flies",
]


def benchmark_endpoints(n=20):
    print("=" * 60)
    print("ENDPOINT BENCHMARK")
    print("=" * 60)
    for method, path in ENDPOINTS:
        times = []
        for _ in range(n):
            start = time.perf_counter()
            if method == "GET":
                client.get(path)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        avg = sum(times) / len(times)
        p50 = sorted(times)[len(times) // 2]
        p95 = sorted(times)[int(len(times) * 0.95)]
        print(f"  {method:4s} {path:<30s} avg={avg:7.1f}ms  p50={p50:7.1f}ms  p95={p95:7.1f}ms")


def benchmark_recommendations(n=20):
    print("\n" + "=" * 60)
    print("RECOMMENDATION LATENCY")
    print("=" * 60)
    times = []
    for _ in range(n):
        title = random.choice(SAMPLE_TITLES)
        start = time.perf_counter()
        client.post("/recommend", json={"title": title})
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    avg = sum(times) / len(times)
    p50 = sorted(times)[len(times) // 2]
    p95 = sorted(times)[int(len(times) * 0.95)]
    mn = min(times)
    mx = max(times)
    print(f"  POST /recommend  avg={avg:7.1f}ms  min={mn:7.1f}ms  max={mx:7.1f}ms")
    print(f"                   p50={p50:7.1f}ms  p95={p95:7.1f}ms")


def benchmark_cache(n=20):
    print("\n" + "=" * 60)
    print("LRU CACHE EFFECT (same title)")
    print("=" * 60)
    _cached_recommend.cache_clear()
    title = "1984"

    start = time.perf_counter()
    client.post("/recommend", json={"title": title})
    cold = (time.perf_counter() - start) * 1000

    times = []
    for _ in range(n):
        start = time.perf_counter()
        client.post("/recommend", json={"title": title})
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    avg = sum(times) / len(times)
    print(f"  Cold call:  {cold:7.1f}ms")
    print(f"  Cached avg: {avg:7.1f}ms  (speedup: {cold/avg:.1f}x)")
    print(f"  Cache info: {_cached_recommend.cache_info()}")


def check_security_headers():
    print("\n" + "=" * 60)
    print("SECURITY HEADERS")
    print("=" * 60)
    resp = client.get("/health")
    headers = {
        "x-content-type-options": resp.headers.get("x-content-type-options"),
        "x-frame-options": resp.headers.get("x-frame-options"),
        "x-xss-protection": resp.headers.get("x-xss-protection"),
        "referrer-policy": resp.headers.get("referrer-policy"),
    }
    for name, value in headers.items():
        status = "OK" if value else "MISSING"
        print(f"  {name:<30s} = {value or '(none)':<30s} [{status}]")


def check_health():
    print("\n" + "=" * 60)
    print("HEALTH CHECK")
    print("=" * 60)
    resp = client.get("/health")
    data = resp.json()
    for k, v in data.items():
        print(f"  {k:<20s} = {v}")


if __name__ == "__main__":
    benchmark_endpoints()
    benchmark_recommendations()
    benchmark_cache()
    check_security_headers()
    check_health()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
