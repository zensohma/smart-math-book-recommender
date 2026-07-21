# Product Requirements Document (PRD)

# 📚 Smart Mathematics Book Recommender

Version: 1.0

Status: In Progress

Author: Hada

Date: July 2026

---

# 📌 Product Overview

## Product Description

Smart Mathematics Book Recommender adalah sistem rekomendasi buku matematika berbasis machine learning yang membantu mahasiswa menemukan buku yang relevan berdasarkan minat, riwayat pencarian, dan topik matematika yang diminati.

Sistem dirancang untuk membantu mahasiswa mengatasi kesulitan dalam memilih referensi belajar yang tepat dari banyaknya buku matematika yang tersedia.

---

# 🚨 Problem Statement

Mahasiswa matematika sering mengalami kesulitan dalam menemukan buku yang sesuai dengan kebutuhan belajar mereka.

Beberapa permasalahan yang umum terjadi:

- Terlalu banyak pilihan buku.
- Sulit menentukan buku yang sesuai dengan level kemampuan.
- Tidak mengetahui hubungan antar topik matematika.
- Menghabiskan banyak waktu mencari referensi.
- Rekomendasi dari internet sering tidak spesifik untuk mahasiswa matematika.

Akibatnya:

- Proses belajar menjadi kurang efisien.
- Mahasiswa menggunakan referensi yang kurang tepat.
- Motivasi belajar menurun.

---

# 🌟 Product Vision

Menjadi platform rekomendasi buku matematika yang cerdas dan personal bagi mahasiswa, dosen, serta pembelajar matematika di Indonesia.

---

# 🎯 Goals

## Business Goals

- Menyediakan sistem rekomendasi buku matematika yang mudah digunakan.
- Meningkatkan efisiensi pencarian referensi belajar.
- Menjadi portofolio machine learning end-to-end.

## Technical Goals

- [x] Membangun recommendation system berbasis machine learning.
- [x] Menyediakan REST API untuk rekomendasi.
- [x] Men-deploy sistem ke cloud.

---

# 🙋 User Goals

Pengguna ingin:

- Menemukan buku yang relevan dengan cepat.
- Mendapat rekomendasi buku berdasarkan minat.
- Menemukan buku lanjutan setelah mempelajari suatu topik.
- Menjelajahi referensi matematika secara lebih terstruktur.

---

# 👥 Target Users

## Primary Users

### Mahasiswa Matematika

Karakteristik:

- Semester 1–8
- Sedang mengambil mata kuliah matematika
- Membutuhkan referensi belajar

Pain Points:

- Bingung memilih buku
- Tidak tahu buku terbaik untuk topik tertentu

---

### Mahasiswa Data Science / Machine Learning

Karakteristik:

- Belajar matematika untuk AI
- Membutuhkan referensi tambahan

Pain Points:

- Sulit menemukan buku matematika yang sesuai kebutuhan ML

---

## Secondary Users

### Dosen

Tujuan:

- Memberikan rekomendasi buku kepada mahasiswa.

### Pembelajar Mandiri

Tujuan:

- Belajar matematika secara otodidak.

---

# 📦 Scope

## In Scope (MVP)

- [x] Pencarian buku
- [x] Rekomendasi buku serupa
- [x] Detail buku
- [x] Content-Based Recommendation
- [x] REST API
- [x] Dashboard web (basic)

## Out of Scope

- User Authentication
- Social Features
- Rating System
- Mobile Application

---

# 📖 User Stories

## US-001

Sebagai mahasiswa,

Saya ingin mencari buku matematika,

Sehingga saya dapat menemukan referensi yang relevan.

Acceptance Criteria:

- Pengguna dapat memasukkan judul buku.
- Sistem menampilkan hasil pencarian.

Status: [x] Done (components/SearchBar.tsx + app/search/page.tsx)

---

## US-002

Sebagai mahasiswa,

Saya ingin mendapatkan rekomendasi buku serupa,

Sehingga saya dapat memperluas referensi belajar.

Acceptance Criteria:

- Sistem menampilkan minimal 5 rekomendasi.
- Rekomendasi berdasarkan kemiripan topik.

Status: [x] Done (notebook 03 + ml/recommender.py)

---

## US-003

Sebagai mahasiswa,

Saya ingin melihat detail buku,

Sehingga saya dapat menentukan apakah buku tersebut sesuai kebutuhan.

Acceptance Criteria:

- Menampilkan judul.
- Menampilkan penulis.
- Menampilkan kategori.
- Menampilkan deskripsi.

Status: [x] Done (app/recommendations/[id]/page.tsx)

---

# 🤖 Machine Learning Requirements

## Recommendation Approach

### Phase 1

Content-Based Filtering

Metode:

- [x] TF-IDF
- [x] Cosine Similarity (via NearestNeighbors metric="cosine")

Input:

- Judul buku
- Deskripsi buku
- Kategori

Output:

- Daftar buku yang mirip

Status: [x] Done

---

### Phase 2

Collaborative Filtering

Metode:

- Matrix Factorization
- SVD

Input:

- Riwayat rating pengguna

Output:

- Personalized Recommendation

Status: [ ] Belum dikerjakan

---

# 📊 Dataset Requirements

## Dataset Source

[x] Goodreads Dataset

---

## Required Fields

| Field | Type | Status |
|---------|---------|--------|
| book_id | Integer | [x] Done |
| title | String | [x] Done |
| author | String | [x] Done |
| category | String | [x] Done (genres) |
| description | Text | [x] Done |
| rating | Float | [ ] Not available in dataset |

---

# ⚙ Functional Requirements

## FR-001 Search Book

Deskripsi:

Pengguna dapat mencari buku berdasarkan judul.

Input:

- Judul Buku

Output:

- Daftar buku

Status: [x] Done (app/search/page.tsx + components/SearchBar.tsx)

---

## FR-002 Book Recommendation

Deskripsi:

Sistem memberikan rekomendasi buku berdasarkan kemiripan.

Input:

- Judul Buku

Output:

- Top 5 rekomendasi

Status: [x] Done (ml/recommender.py + backend/recommender_service.py)

---

## FR-003 Book Detail

Deskripsi:

Menampilkan informasi lengkap buku.

Output:

- Judul
- Penulis
- Kategori
- Deskripsi

Status: [x] Done (app/recommendations/[id]/page.tsx)

---

# 🔒 Non Functional Requirements

## Performance

- [x] Response API < 1 detik (LRU cache, GZip, request timing middleware)
- [x] Recommendation < 2 detik (KNN brute-force + LRU cache maxsize=2048)

## Reliability

- [ ] Availability 99%

## Scalability

- [ ] Mendukung minimal 1.000 pengguna

## Security

- [x] HTTPS (via deployment platform)
- [x] Rate Limiting (slowapi, configurable per-route limits)

---

# 🎨 Screen Requirements

## Home Page

Components:

- [x] Search Bar (page.tsx)
- [x] Recommended Books
- [x] Popular Books

---

## Search Result Page

Components:

- [x] List Buku
- [x] Filter Kategori
- [x] Search Input

---

## Recommendation Page

Components:

- [x] Detail Buku
- [x] Similar Books
- [x] Recommendation List

---

# 🔌 API Requirements

## GET /books

Mengambil daftar buku.

Status: [x] Done (backend/app.py:21)

---

## GET /books/{id}

Mengambil detail buku.

Status: [x] Done (backend/app.py:29)

---

## POST /recommend

Request

{
  "title": "Linear Algebra Done Right"
}

Response

{
  "recommendations": [
    "Matrix Analysis",
    "Advanced Linear Algebra",
    "Numerical Linear Algebra"
  ]
}

Status: [x] Done (backend/recommender_service.py)

---

# 🏗 Tech Stack

## Data Processing

- [x] Pandas
- [x] NumPy

## Machine Learning

- [x] Scikit-Learn
- [x] TF-IDF
- [x] Cosine Similarity

## Backend

- [x] FastAPI

## Frontend

- [x] Next.js
- [x] TypeScript
- [x] Tailwind CSS
- [x] Shadcn UI

## Database

- [x] MySQL

## Deployment

- [x] Docker
- [ ] Railway
- [ ] Vercel

---

# 📈 Success Metrics

## Product Metrics

- Minimal 100 buku direkomendasikan dengan benar.

## ML Metrics

- [x] Precision@5 > 80%
- [x] Recall@5 > 75%

---

# 🗺 Roadmap

## Phase 1

- [x] Dataset Collection
- [x] Data Cleaning

## Phase 2

- [x] EDA
- [x] Feature Engineering

## Phase 3

- [x] Content-Based Recommendation

## Phase 4

- [x] FastAPI Development

## Phase 5

- [x] Frontend Development (basic)

## Phase 6

- [x] Dockerization

## Phase 7

- [ ] Deployment

## Phase 8

- [ ] Collaborative Filtering

---

# 🚀 Future Features

- Personalized Recommendation
- User Rating System
- AI Chat Assistant
- Learning Path Recommendation
- Mathematics Knowledge Graph
