# Architecture

Arsitektur sistem Smart Mathematics Book Recommender.

## System Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend   │────▶│   Backend    │────▶│   MySQL     │
│  (Next.js)   │     │  (FastAPI)   │     │  Database   │
│  Port 3000   │     │  Port 8000   │     │  Port 3306  │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │  ML Models   │
                    │  (pickle)    │
                    └──────────────┘
```

## Component Breakdown

### Frontend (`frontend/`)

Next.js app dengan 3 halaman:

| Route | Fungsi |
|-------|--------|
| `/` | Homepage - search bar, rekomendasi featured, buku populer |
| `/search?q=...` | Hasil pencarian dengan filter genre |
| `/recommendations/[id]` | Detail buku + 5 buku serupa |

API client di `src/lib/api.ts` dengan timeout 10 detik per request.

### Backend (`backend/`)

FastAPI server dengan 7 endpoints:

| Endpoint | Fungsi |
|----------|--------|
| `GET /health` | Health check |
| `GET /books` | List/search buku |
| `GET /books/popular` | Buku populer |
| `GET /books/{id}` | Detail buku |
| `GET /genres` | Daftar genre |
| `POST /recommend` | Rekomendasi buku |
| `GET /recommend/featured` | Rekomendasi random |

**Graceful Degradation:** Kalau database down, backend fallback ke data in-memory dari pickle files.

### ML Models (`ml/`)

Content-based recommendation menggunakan:

1. **TF-IDF** - Vectorize konten buku (judul + penulis + genre + deskripsi)
2. **KNN (K=6)** - Cari 6 tetangga terdekat berdasarkan cosine similarity
3. **LRU Cache** - Cache hasil rekomendasi (max 2048 entries)

Artifacts tersimpan di `ml/models/`:
- `knn_model.pkl` - Model KNN
- `tfidf.pkl` - TF-IDF vectorizer
- `tfidf_matrix.pkl` - Sparse matrix hasil vectorisasi
- `books.pkl` - DataFrame buku
- `title_to_index.pkl` - Mapping judul ke index

### Database (`backend/models.py`)

4 tabel:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  users   │────▶│ ratings  │◀────│  books   │
└──────────┘     └──────────┘     └──────────┘
     │
     ▼
┌──────────────┐
│search_history│
└──────────────┘
```

- `books` - 14.987 buku (title, author, genres, description)
- `users` - Belum digunakan (persiapan Phase 2)
- `ratings` - Belum digunakan (persiapan collaborative filtering)
- `search_history` - Belum digunakan

## Data Flow

### Search Flow
```
User ketik query → Frontend GET /books?q=... → Backend query MySQL → Return results
```

### Recommendation Flow
```
User klik buku → Frontend POST /recommend → Backend load pickle files
→ TF-IDF vectorize → KNN query → Return top-5 + similarity scores
```

### Feature Engineering
```
title + " " + author + " " + genres×3 + " " + genres×2 + " " + genres + " " + description
                                                              ↓
                                                    TF-IDF Vectorizer
                                                              ↓
                                                    KNN (cosine distance)
```

Genre diulang 3x dan 2x untuk memberi bobot lebih tinggi pada TF-IDF.

## Middleware Stack

```
Request → Security Headers → GZip → Rate Limiter → CORS → Endpoint
```

| Middleware | Fungsi |
|-----------|--------|
| Security Headers | Tambah X-Content-Type-Options, X-Frame-Options, dll |
| GZip | Kompresi response |
| Rate Limiter | Batasi request per menit per IP |
| CORS | Allow cross-origin dari frontend |
| Request Logger | Log method, path, status, elapsed time |
