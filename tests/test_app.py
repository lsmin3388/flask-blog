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


class TestCRUD:
    def test_create_page_returns_200(self, client):
        response = client.get('/create')
        assert response.status_code == 200

    def test_create_post(self, client):
        response = client.post('/create', data={
            'title': '새 글',
            'content': '새 글 내용',
            'category': 'tech'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '새 글'.encode() in response.data

    def test_edit_page_returns_200(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('수정할 글', '내용', 'general')
            )
            db.commit()
            response = client.get('/edit/1')
            assert response.status_code == 200
            assert '수정할 글'.encode() in response.data

    def test_edit_post(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('원본 글', '원본 내용', 'general')
            )
            db.commit()
        response = client.post('/edit/1', data={
            'title': '수정된 글',
            'content': '수정된 내용',
            'category': 'tech'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert '수정된 글'.encode() in response.data

    def test_delete_post(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('삭제할 글', '내용', 'general')
            )
            db.commit()
        response = client.post('/delete/1', follow_redirects=True)
        assert response.status_code == 200
        assert '삭제할 글'.encode() not in response.data


class TestDetail:
    def test_post_detail_returns_200(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('상세 글', '상세 내용입니다', 'tech')
            )
            db.commit()
        response = client.get('/post/1')
        assert response.status_code == 200

    def test_post_detail_shows_content(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('상세 글', '상세 내용입니다', 'tech')
            )
            db.commit()
        response = client.get('/post/1')
        assert '상세 글'.encode() in response.data
        assert '상세 내용입니다'.encode() in response.data

    def test_post_detail_not_found(self, client):
        response = client.get('/post/999')
        assert response.status_code == 404


class TestStats:
    def test_stats_page_returns_200(self, client):
        response = client.get('/stats')
        assert response.status_code == 200

    def test_stats_shows_total_count(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('글1', '내용', 'tech')
            )
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('글2', '내용', 'life')
            )
            db.commit()
        response = client.get('/stats')
        assert response.status_code == 200
        data = response.data.decode()
        assert '2' in data

    def test_stats_shows_category_count(self, client):
        with app.app_context():
            db = get_db()
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('글1', '내용', 'tech')
            )
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('글2', '내용', 'tech')
            )
            db.execute(
                "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
                ('글3', '내용', 'life')
            )
            db.commit()
        response = client.get('/stats')
        data = response.data.decode()
        assert 'tech' in data
        assert 'life' in data
