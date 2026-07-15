# Machine Learning Pipeline

Dokumentasi pipeline machine learning untuk content-based book recommendation.

## Overview

Sistem menggunakan **Content-Based Filtering** dengan dua komponen utama:

1. **TF-IDF** - Mengubah teks buku menjadi vektor numerik
2. **K-Nearest Neighbors** - Mencari buku paling mirip berdasarkan cosine similarity

## Pipeline

```
CSV Dataset
    │
    ▼
Data Cleaning (notebook 02)
    │
    ▼
Feature Engineering (train.py)
    │
    ├── title + author + genres×3 + genres×2 + genres + description
    │
    ▼
TF-IDF Vectorization (max 10.000 features)
    │
    ▼
KNN Model (K=6, cosine, brute force)
    │
    ▼
Save artifacts (.pkl)
```

## Training

### Command

```bash
cd backend
python -m ml.train --input ../data/processed/books_for_ml.csv
```

### CLI Arguments

| Argument | Default | Deskripsi |
|----------|---------|-----------|
| `--input` | `data/processed/books_for_ml.csv` | Path ke CSV |
| `--output` | `ml/models/` | Output directory |
| `--max-features` | 10000 | Max TF-IDF features |
| `--n-neighbors` | 6 | Jumlah neighbors KNN |
| `--raw-data` | None | Path ke raw CSV untuk genre extraction |

### Output Artifacts

| File | Deskripsi |
|------|-----------|
| `knn_model.pkl` | Fitted NearestNeighbors model |
| `tfidf.pkl` | Fitted TfidfVectorizer |
| `tfidf_matrix.pkl` | Sparse TF-IDF matrix (14987 x 10000) |
| `books.pkl` | Books DataFrame |
| `title_to_index.pkl` | Series mapping title → matrix index |

## Inference

### Function Signature

```python
def recommend(book_title, books, model, tfidf_matrix,
              title_to_index, top_n=5, n_candidates=50):
```

### Logic

1. Cari index buku dari `title_to_index`
2. Query KNN dengan `n_neighbors=50` (ambil kandidat lebih banyak)
3. Hitung similarity: `(1 - distance) * 100`
4. Skip buku pertama (self-match)
5. Deduplicate judul
6. Return top-N hasil

### Backend Adapter

`recommender_service.py` memuat semua artifacts saat import, lalu expose fungsi:

```python
recommend(book_title, top_n=5) -> list[dict]
```

Response:
```python
[
    {"title": "...", "author": "...", "similarity": 87.5},
    ...
]
```

## Feature Engineering

Format input ke TF-IDF:

```
{title} {author} {genres} {genres} {genres} {genres} {genres} {description}
         ↑                                          ↑         ↑
      genres 1x                                 genres 2x  genres 3x
```

Genre diulang untuk memberi bobot lebih tinggi dalam vektor TF-IDF, karena genre merupakan fitur paling discriminative untuk rekomendasi buku.

## Hyperparameters

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| `max_features` | 10.000 | Cukup untuk menangkap vocabulary penting, batasi noise |
| `n_neighbors` | 6 | 5 rekomendasi + 1 self-match |
| `metric` | cosine | Cocok untuk text similarity, ignore magnitude |
| `algorithm` | brute | Optimal untuk sparse high-dimensional data |

## Evaluation

Metrik yang digunakan (notebook 04):

| Metrik | Target | Deskripsi |
|--------|--------|-----------|
| Precision@5 | > 80% | Fraction rekomendasi yang share genre dengan query |
| Recall@5 | > 75% | Fraction genre query yang muncul di rekomendasi |
| Hit Rate@5 | - | % queries yang punya minimal 1 rekomendasi relevan |
| NDCG@5 | - | Ranking quality (normalized) |
| MRR | - | Rata-rata reciprocal rank |

Evaluasi dilakukan pada sample 500 buku secara random.

## Notebooks

| Notebook | Isi |
|----------|-----|
| `01_data_understanding` | EDA - cek null, duplikat, genre structure |
| `02_data_cleaning` | Pilih kolom, hapus duplikat, export CSV |
| `03_recommendation_engine` | Prototipe TF-IDF + KNN, save artifacts |
| `04_model_evaluation` | Hitung Precision@5, Recall@5, dll |
