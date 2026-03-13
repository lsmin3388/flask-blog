import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'

    with app.test_client() as client:
        from models import init_db
        init_db(app)
        yield client
