import logging
import os
import sys
import joblib
import pandas as pd

logger = logging.getLogger(__name__)

_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "ml", "models")

model = None
books = None
title_to_index = None
tfidf_matrix = None

try:
    model = joblib.load(os.path.join(_MODEL_DIR, "knn_model.pkl"))
    books = joblib.load(os.path.join(_MODEL_DIR, "books.pkl"))
    title_to_index = joblib.load(os.path.join(_MODEL_DIR, "title_to_index.pkl"))
    tfidf_matrix = joblib.load(os.path.join(_MODEL_DIR, "tfidf_matrix.pkl"))
except Exception as e:
    logger.error("Failed to load ML model files: %s", e)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ml.recommender import recommend as _recommend


def recommend(book_title, top_n=5):
    if model is None or books is None or tfidf_matrix is None or title_to_index is None:
        return []
    df = _recommend(book_title, books, model, tfidf_matrix, title_to_index, top_n=top_n)
    return df.to_dict(orient="records")
