# Setup Guide

Panduan installasi dan menjalankan proyek secara lokal.

## Prerequisites

- Python 3.10+
- Node.js 18+
- MySQL 8.0+

## 1. Database MySQL

```sql
CREATE DATABASE smart_math_book;
```

Root user default tanpa password. Kalau pakai password, update di `.env` dan `backend/alembic.ini`.

## 2. Backend

```bash
cd backend

# Buat virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy ..\.env.example ..\.env
# Edit ..\.env sesuai kebutuhan

# Jalankan migration
alembic upgrade head

# Seed database (~15.000 buku)
python seed_db.py --reset

# Jalankan server
uvicorn app:app --reload --port 8000
```

API tersedia di `http://localhost:8000/docs` (Swagger UI).

## 3. Frontend

```bash
cd frontend

npm install
npm run dev
```

Frontend tersedia di `http://localhost:3000`.

## 4. Environment Variables

Buat file `.env` di root project:

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `DATABASE_URL` | `mysql+pymysql://root@localhost:3306/smart_math_book` | Koneksi database |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |
| `ENABLE_GZIP` | `true` | Aktifkan GZip compression |
| `ENABLE_SECURITY_HEADERS` | `true` | Aktifkan security headers |
| `RATE_LIMIT_DEFAULT` | `60/minute` | Rate limit default |
| `RATE_LIMIT_RECOMMEND` | `20/minute` | Rate limit untuk `/recommend` |

Untuk frontend, set `NEXT_PUBLIC_API_URL` kalau backend tidak di `localhost:8000`.

## 5. Training Model (Optional)

Model sudah pre-trained. Untuk re-train:

```bash
cd backend
python -m ml.train --input ../data/processed/books_for_ml.csv
```

Artifacts tersimpan di `ml/models/`.

## 6. Running Tests

```bash
cd tests

# Install dev dependencies
pip install -r ../backend/requirements-dev.txt

# Jalankan semua test
pytest

# Jalankan benchmark
python benchmark.py
```
