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


def get_post(post_id):
    db = get_db()
    return db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()


def create_post(title, content, category='general'):
    db = get_db()
    db.execute(
        "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
        (title, content, category)
    )
    db.commit()


def update_post(post_id, title, content, category):
    db = get_db()
    db.execute(
        "UPDATE posts SET title = ?, content = ?, category = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (title, content, category, post_id)
    )
    db.commit()


def delete_post(post_id):
    db = get_db()
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()
