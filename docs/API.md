# API Reference

Base URL: `http://localhost:8000`

Swagger docs: `http://localhost:8000/docs`

---

## Health Check

### `GET /health`

Status sistem dan koneksi database.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "database_connected": true,
  "total_books": 14987
}
```

| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `status` | string | `"ok"` atau `"degraded"` kalau model tidak termuat |
| `model_loaded` | bool | ML model berhasil di-load |
| `database_connected` | bool | Database bisa diakses |
| `total_books` | int | Jumlah buku di database |

---

## Books

### `GET /books`

Mengambil daftar buku. Kalau ada parameter `q`, filter berdasarkan judul.

**Query Parameters:**

| Parameter | Tipe | Wajib | Deskripsi |
|-----------|------|-------|-----------|
| `q` | string | Tidak | Filter judul buku (ILIKE match) |

**Response:**
```json
[
  {
    "bookId": 1,
    "title": "Linear Algebra Done Right",
    "author": "Sheldon Axler",
    "genres": "Mathematics, Linear Algebra",
    "description": "..."
  }
]
```

**Notes:**
- Tanpa `q`: return 50 buku pertama
- Dengan `q`: max 20 hasil, partial match pada judul

---

### `GET /books/popular`

Mengambil buku populer (berdasarkan urutan database).

**Query Parameters:**

| Parameter | Tipe | Default | Deskripsi |
|-----------|------|---------|-----------|
| `limit` | int | 6 | Jumlah buku (1-50) |

**Response:** Array of book objects.

---

### `GET /books/{book_id}`

Detail satu buku berdasarkan ID.

**Path Parameters:**

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| `book_id` | int | ID buku |

**Response:** Book object.

**Error:**
- `404` - Buku tidak ditemukan

---

## Genres

### `GET /genres`

Daftar genre yang tersedia (hardcoded).

**Response:**
```json
[
  "Calculus",
  "Computation",
  "Computer Science",
  "Engineering",
  "Logic",
  "Mathematics",
  "Physics",
  "Programming",
  "Statistics"
]
```

---

## Recommendations

### `POST /recommend`

Mendapatkan 5 buku serupa berdasarkan judul.

**Request Body:**
```json
{
  "title": "Linear Algebra Done Right"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "title": "Matrix Analysis",
      "author": "Roger A. Horn",
      "similarity": 87.5
    },
    {
      "title": "Advanced Linear Algebra",
      "author": "Steven Roman",
      "similarity": 82.3
    }
  ]
}
```

| Field | Tipe | Deskripsi |
|-------|------|-----------|
| `similarity` | float | Persentase kemiripan (0-100) |

**Errors:**
- `400` - Judul kosong
- `404` - Buku tidak ditemukan

**Rate Limit:** 20/minute

---

### `GET /recommend/featured`

Rekomendasi random untuk ditampilkan di homepage.

**Response:**
```json
{
  "book": {
    "bookId": 42,
    "title": "1984",
    "author": "George Orwell"
  },
  "recommendations": [
    {
      "title": "Animal Farm",
      "author": "George Orwell",
      "similarity": 75.2
    }
  ]
}
```

**Notes:**
- Mengambil 1 buku random + 6 rekomendasi
- Hasil di-cache 5 menit

---

## Error Responses

Semua error mengikuti format:

```json
{
  "detail": "pesan error"
}
```

## Rate Limiting

| Endpoint | Limit |
|----------|-------|
| Default (semua GET) | 60/minute |
| `POST /recommend` | 20/minute |

Rate limit berdasarkan IP address.

## Security Headers

Setiap response menambahkan:

| Header | Value |
|--------|-------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
