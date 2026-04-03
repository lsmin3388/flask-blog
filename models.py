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


def _build_post_query(category=None):
    where_clause = ""
    params = []
    if category:
        where_clause = " WHERE category = ?"
        params.append(category)
    return where_clause, params


def get_all_posts(category=None, page=None, per_page=5):
    db = get_db()
    where_clause, params = _build_post_query(category)

    if page is None:
        posts = db.execute(
            f"SELECT * FROM posts{where_clause} ORDER BY created_at DESC",
            params
        ).fetchall()
        return posts

    total = db.execute(
        f"SELECT COUNT(*) as count FROM posts{where_clause}",
        params
    ).fetchone()['count']
    posts = db.execute(
        f"SELECT * FROM posts{where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page]
    ).fetchall()

    total_pages = (total + per_page - 1) // per_page
    return {
        'posts': posts,
        'page': page,
        'total_pages': total_pages,
        'total': total
    }


def search_posts(query):
    db = get_db()
    posts = db.execute(
        "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC",
        (f'%{query}%', f'%{query}%')
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


def get_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) as count FROM posts").fetchone()['count']
    by_category = db.execute(
        "SELECT category, COUNT(*) as count FROM posts GROUP BY category ORDER BY count DESC"
    ).fetchall()
    by_month = db.execute(
        "SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count "
        "FROM posts GROUP BY month ORDER BY month DESC"
    ).fetchall()
    return {
        'total': total,
        'by_category': by_category,
        'by_month': by_month
    }
