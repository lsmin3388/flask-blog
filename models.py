import sqlite3

from flask import g


SCHEMA = '''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
'''


def get_db():
    if 'db' not in g:
        from flask import current_app
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = sqlite3.connect(app.config['DATABASE'])
        db.execute(SCHEMA)
        db.commit()
        db.close()


def get_all_posts(category=None):
    db = get_db()
    if category:
        posts = db.execute(
            "SELECT * FROM posts WHERE category = ? ORDER BY created_at DESC",
            (category,)
        ).fetchall()
    else:
        posts = db.execute(
            "SELECT * FROM posts ORDER BY created_at DESC"
        ).fetchall()
    return posts
