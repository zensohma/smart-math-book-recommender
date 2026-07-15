import argparse
import os
import sys

import pandas as pd
from sqlalchemy import text

from database import engine, SessionLocal
from models import Base, Book


def seed(input_path: str, reset: bool = False):
    if reset:
        print("Dropping and recreating tables...")
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    print(f"Reading {input_path}...")
    df = pd.read_csv(input_path)
    df = df.drop_duplicates(subset=["title"]).reset_index(drop=True)
    print(f"  {len(df)} buku setelah dedup")

    session = SessionLocal()
    try:
        existing = session.query(Book).count()
        if existing > 0 and not reset:
            print(f"  Database sudah ada {existing} buku. Gunakan --reset untuk reset.")
            return

        batch_size = 500
        total = len(df)
        for i in range(0, total, batch_size):
            batch = df.iloc[i : i + batch_size]
            books = []
            for _, row in batch.iterrows():
                books.append(
                    Book(
                        id=int(row["bookId"]),
                        title=str(row["title"]),
                        author=str(row["author"]),
                        genres=str(row.get("genres", "")),
                        description=str(row.get("description", "")),
                    )
                )
            session.bulk_save_objects(books)
            session.commit()
            done = min(i + batch_size, total)
            print(f"  Inserted {done}/{total}")

        print("Seed selesai.")
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database from CSV")
    parser.add_argument(
        "--input",
        default="../data/processed/books_for_ml.csv",
        help="Path ke CSV dataset",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop dan recreate tabel sebelum seed",
    )
    args = parser.parse_args()
    seed(args.input, args.reset)
