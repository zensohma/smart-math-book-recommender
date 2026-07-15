import pandas as pd
from ml.recommender import recommend


def _load():
    import joblib
    import os
    model_dir = os.path.join(os.path.dirname(__file__), "..", "ml", "models")
    model = joblib.load(os.path.join(model_dir, "knn_model.pkl"))
    books = joblib.load(os.path.join(model_dir, "books.pkl"))
    title_to_index = joblib.load(os.path.join(model_dir, "title_to_index.pkl"))
    tfidf_matrix = joblib.load(os.path.join(model_dir, "tfidf_matrix.pkl"))
    return books, model, tfidf_matrix, title_to_index


BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX = _load()


def test_recommend_returns_dataframe():
    result = recommend("1984", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX)
    assert isinstance(result, pd.DataFrame)


def test_recommend_returns_top_n():
    result = recommend("1984", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX, top_n=3)
    assert len(result) <= 3


def test_recommend_has_columns():
    result = recommend("1984", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX)
    assert "title" in result.columns
    assert "author" in result.columns
    assert "similarity" in result.columns


def test_recommend_similarity_range():
    result = recommend("1984", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX)
    assert (result["similarity"] >= 0).all()
    assert (result["similarity"] <= 100).all()


def test_recommend_unknown_book():
    result = recommend("Buku Tidak Ada XYZ123", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_recommend_not_duplicate_titles():
    result = recommend("1984", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX, top_n=10)
    assert result["title"].is_unique


def test_recommend_harry_potter():
    result = recommend("Harry Potter and the Sorcerer's Stone", BOOKS, MODEL, TFIDF_MATRIX, TITLE_TO_INDEX)
    titles = result["title"].tolist()
    assert any("Harry Potter" in t for t in titles)


def test_precision_at_5_above_80_percent():
    import numpy as np
    import pandas as pd
    import os

    raw_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "books.csv")
    if not os.path.exists(raw_path):
        return

    raw = pd.read_csv(raw_path)
    GLOBAL_SUFFIX = "Young Adult"

    def extract_book_genres(genres_str):
        if pd.isna(genres_str):
            return []
        parts = genres_str.split(",")
        last_global_idx = -1
        for i, p in enumerate(parts):
            if p.strip() == GLOBAL_SUFFIX:
                last_global_idx = i
        return list(set(g.strip() for g in parts[last_global_idx + 1:] if g.strip()))

    raw["book_genres"] = raw["genres"].apply(extract_book_genres)
    genre_map = raw.set_index("bookId")["book_genres"].to_dict()
    books_df = BOOKS.copy()
    books_df["genres_clean"] = books_df["bookId"].map(genre_map).apply(
        lambda x: x if isinstance(x, list) else []
    )
    books_df["num_genres"] = books_df["genres_clean"].apply(len)

    eval_books = books_df[books_df["num_genres"] >= 2]
    np.random.seed(42)
    sample_idx = np.random.choice(len(eval_books), size=min(100, len(eval_books)), replace=False)
    sample = eval_books.iloc[sample_idx]

    precision_scores = []
    for _, row in sample.iterrows():
        title = row["title"]
        query_genres = set(row["genres_clean"])
        if title not in TITLE_TO_INDEX:
            continue
        book_idx = TITLE_TO_INDEX[title]
        _, indices = MODEL.kneighbors(TFIDF_MATRIX[book_idx], n_neighbors=6)
        rec_indices = indices[0][1:]
        hits = sum(1 for ri in rec_indices[:5] if set(books_df.iloc[ri]["genres_clean"]) & query_genres)
        precision_scores.append(hits / 5)

    mean_p5 = np.mean(precision_scores)
    assert mean_p5 >= 0.80, f"Precision@5={mean_p5:.4f}, expected >= 0.80"


def test_recall_at_5_above_75_percent():
    import numpy as np
    import pandas as pd
    import os

    raw_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "books.csv")
    if not os.path.exists(raw_path):
        return

    raw = pd.read_csv(raw_path)
    GLOBAL_SUFFIX = "Young Adult"

    def extract_book_genres(genres_str):
        if pd.isna(genres_str):
            return []
        parts = genres_str.split(",")
        last_global_idx = -1
        for i, p in enumerate(parts):
            if p.strip() == GLOBAL_SUFFIX:
                last_global_idx = i
        return list(set(g.strip() for g in parts[last_global_idx + 1:] if g.strip()))

    raw["book_genres"] = raw["genres"].apply(extract_book_genres)
    genre_map = raw.set_index("bookId")["book_genres"].to_dict()
    books_df = BOOKS.copy()
    books_df["genres_clean"] = books_df["bookId"].map(genre_map).apply(
        lambda x: x if isinstance(x, list) else []
    )
    books_df["num_genres"] = books_df["genres_clean"].apply(len)

    eval_books = books_df[books_df["num_genres"] >= 2]
    np.random.seed(42)
    sample_idx = np.random.choice(len(eval_books), size=min(100, len(eval_books)), replace=False)
    sample = eval_books.iloc[sample_idx]

    recall_scores = []
    for _, row in sample.iterrows():
        title = row["title"]
        query_genres = set(row["genres_clean"])
        if title not in TITLE_TO_INDEX or not query_genres:
            continue
        book_idx = TITLE_TO_INDEX[title]
        _, indices = MODEL.kneighbors(TFIDF_MATRIX[book_idx], n_neighbors=6)
        rec_indices = indices[0][1:]
        covered = set()
        for ri in rec_indices[:5]:
            covered |= set(books_df.iloc[ri]["genres_clean"]) & query_genres
        recall_scores.append(len(covered) / len(query_genres))

    mean_r5 = np.mean(recall_scores)
    assert mean_r5 >= 0.75, f"Recall@5={mean_r5:.4f}, expected >= 0.75"
