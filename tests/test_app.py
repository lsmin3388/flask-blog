import os
import sqlite3
import tempfile

import pytest

from app import app
from models import get_db


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path

    with app.app_context():
        db = sqlite3.connect(db_path)
        db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()
        db.close()

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(db_path)


class TestIndex:
    def test_index_page_returns_200(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_index_page_contains_title(self, client):
        response = client.get('/')
        assert '글 목록'.encode() in response.data

    def test_index_page_shows_posts(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('테스트 글', '테스트 내용', 'tech')
            )
            db.commit()
            response = client.get('/')
            assert '테스트 글'.encode() in response.data

    def test_index_page_filter_by_category(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('기술 글', '내용', 'tech')
            )
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('일상 글', '내용', 'life')
            )
            db.commit()
            response = client.get('/?category=tech')
            assert '기술 글'.encode() in response.data
            assert '일상 글'.encode() not in response.data
