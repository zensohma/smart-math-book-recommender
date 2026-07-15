# Smart Mathematics Book Recommender

Sistem rekomendasi buku matematika berbasis machine learning yang membantu mahasiswa menemukan buku relevan berdasarkan minat dan topik.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, TypeScript, Tailwind CSS, Shadcn UI |
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | MySQL |
| ML | Scikit-Learn (TF-IDF + KNN), Pandas, NumPy |
| Dataset | Goodreads (~15.000 buku) |

## Features

- Pencarian buku berdasarkan judul
- Rekomendasi 5 buku serupa berdasarkan kemiripan konten
- Filter berdasarkan genre
- Detail buku lengkap
- Rate limiting & security headers

## Quick Start

Lihat [docs/SETUP.md](docs/SETUP.md) untuk panduan lengkap.

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python seed_db.py --reset
uvicorn app:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Documentation

- [Setup Guide](docs/SETUP.md)
- [API Reference](docs/API.md)
- [Architecture](docs/ARCHITECTURE.md)
- [ML Pipeline](docs/ML.md)
- [Product Requirements](docs/PRD.md)

## Project Structure

```
smart-math-book-recommender/
├── backend/              # FastAPI backend
│   ├── app.py            # API endpoints
│   ├── database.py       # DB connection
│   ├── models.py         # SQLAlchemy models
│   ├── recommender_service.py  # ML adapter
│   ├── seed_db.py        # DB seeder
│   └── alembic/          # Migrations
├── frontend/             # Next.js frontend
│   ├── app/              # Pages
│   ├── components/       # UI components
│   └── src/lib/          # API client & utils
├── ml/                   # Machine learning
│   ├── train.py          # Model training
│   ├── recommender.py    # Inference
│   └── models/           # Serialized artifacts
├── notebooks/            # Jupyter notebooks
├── tests/                # Test suite
├── data/                 # Dataset
│   ├── raw/              # Original CSV
│   └── processed/        # Cleaned CSV
└── docs/                 # Documentation
```

## Author

**Hada** - July 2026
