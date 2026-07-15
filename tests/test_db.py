import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Book, User, Rating, SearchHistory


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_book(db_session):
    book = Book(id=1, title="Test Book", author="Author", genres="Math", description="Desc")
    db_session.add(book)
    db_session.commit()
    assert db_session.query(Book).count() == 1


def test_create_user(db_session):
    user = User(username="testuser")
    db_session.add(user)
    db_session.commit()
    assert db_session.query(User).count() == 1


def test_create_rating(db_session):
    book = Book(id=1, title="Test", author="A", genres="", description="")
    user = User(username="user1")
    db_session.add_all([book, user])
    db_session.commit()

    rating = Rating(user_id=user.id, book_id=book.id, score=5)
    db_session.add(rating)
    db_session.commit()
    assert db_session.query(Rating).count() == 1


def test_create_search_history(db_session):
    user = User(username="user2")
    db_session.add(user)
    db_session.commit()

    search = SearchHistory(user_id=user.id, query="linear algebra")
    db_session.add(search)
    db_session.commit()
    assert db_session.query(SearchHistory).count() == 1


def test_book_relationships(db_session):
    book = Book(id=1, title="T", author="A", genres="", description="")
    user = User(username="u")
    db_session.add_all([book, user])
    db_session.commit()

    rating = Rating(user_id=user.id, book_id=book.id, score=4)
    db_session.add(rating)
    db_session.commit()

    assert len(book.ratings) == 1
    assert book.ratings[0].score == 4
