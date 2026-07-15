import pandas as pd


def recommend(book_title, books, model, tfidf_matrix, title_to_index, top_n=5, n_candidates=50):
    if book_title not in title_to_index:
        return pd.DataFrame(columns=["title", "author"])

    idx = title_to_index[book_title]

    distances, indices = model.kneighbors(
        tfidf_matrix[idx],
        n_neighbors=n_candidates
    )

    rec_indices = indices[0][1:]
    rec_distances = distances[0][1:]

    recommendations = books.iloc[rec_indices][["title", "author"]].copy()
    recommendations["similarity"] = (1 - rec_distances) * 100

    recommendations = recommendations.drop_duplicates(subset=["title"])

    return recommendations.head(top_n)
