import argparse
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


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


def train(input_path, output_dir, max_features=10000, n_neighbors=6, raw_data_path=None):
    print(f"Loading data from {input_path}...")
    books = pd.read_csv(input_path)
    books = books.drop_duplicates(subset=["title"]).reset_index(drop=True)
    print(f"  Total buku setelah dedup: {len(books)}")

    if raw_data_path and os.path.exists(raw_data_path):
        print(f"Loading raw data for genres from {raw_data_path}...")
        raw = pd.read_csv(raw_data_path)
        raw["book_genres"] = raw["genres"].apply(extract_book_genres)
        genre_map = raw.set_index("bookId")["book_genres"].to_dict()
        books["genres_clean"] = books["bookId"].map(genre_map).apply(
            lambda x: " ".join(x) if isinstance(x, list) else ""
        )
        print(f"  Books with cleaned genres: {(books['genres_clean'] != '').sum()}")
    else:
        books["genres_clean"] = ""

    books["content"] = (
        books["title"].fillna("") + " " +
        books["author"].fillna("") + " " +
        books["genres_clean"].fillna("") + " " * 3 +
        books["genres_clean"].fillna("") + " " * 3 +
        books["genres_clean"].fillna("") + " " +
        books["description"].fillna("")
    )

    print(f"Building TF-IDF matrix (max_features={max_features})...")
    tfidf = TfidfVectorizer(stop_words="english", max_features=max_features)
    tfidf_matrix = tfidf.fit_transform(books["content"])
    print(f"  Matrix shape: {tfidf_matrix.shape}")

    print(f"Training KNN model (n_neighbors={n_neighbors}, metric=cosine)...")
    model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=n_neighbors)
    model.fit(tfidf_matrix)

    title_to_index = pd.Series(
        books.index,
        index=books["title"]
    ).drop_duplicates()

    os.makedirs(output_dir, exist_ok=True)

    artifacts = {
        "knn_model.pkl": model,
        "tfidf.pkl": tfidf,
        "tfidf_matrix.pkl": tfidf_matrix,
        "books.pkl": books,
        "title_to_index.pkl": title_to_index,
    }

    for name, obj in artifacts.items():
        path = os.path.join(output_dir, name)
        joblib.dump(obj, path)
        print(f"  Saved {path}")

    print("Training selesai.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train book recommendation model")
    parser.add_argument(
        "--input",
        default="../data/processed/books_for_ml.csv",
        help="Path ke CSV dataset (default: ../data/processed/books_for_ml.csv)"
    )
    parser.add_argument(
        "--output",
        default="../ml/models",
        help="Directory untuk save model artifacts (default: ../ml/models)"
    )
    parser.add_argument(
        "--max-features",
        type=int,
        default=10000,
        help="Max features untuk TF-IDF (default: 10000)"
    )
    parser.add_argument(
        "--n-neighbors",
        type=int,
        default=6,
        help="Jumlah neighbors untuk KNN (default: 6)"
    )
    parser.add_argument(
        "--raw-data",
        default=None,
        help="Path ke raw CSV untuk extract genres (default: None)"
    )
    args = parser.parse_args()

    train(args.input, args.output, args.max_features, args.n_neighbors, args.raw_data)
