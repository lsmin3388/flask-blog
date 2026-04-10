"""Database access layer for the Flask Blog application.

Provides SQLite-backed CRUD operations for blog posts, including
pagination, search, and statistics queries.
"""

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
    """Get the database connection for the current request.

    Uses Flask's ``g`` object to cache the connection per-request.
    The connection uses ``sqlite3.Row`` as row factory so that
    columns can be accessed by name.

    Returns:
        sqlite3.Connection: The active database connection.
    """
    if 'db' not in g:
        from flask import current_app
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request.

    Args:
        e: An optional exception passed by Flask's teardown mechanism.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(app):
    """Initialize the database and register the teardown hook.

    Creates the posts table if it does not exist and registers
    :func:`close_db` as a teardown handler.

    Args:
        app (Flask): The Flask application instance.
    """
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = sqlite3.connect(app.config['DATABASE'])
        db.execute(SCHEMA)
        db.commit()
        db.close()


def _build_post_query(category=None):
    """Build a WHERE clause for filtering posts by category.

    Args:
        category (str, optional): The category to filter by.

    Returns:
        tuple: A (where_clause, params) pair where *where_clause* is
            an SQL fragment (empty string when no filter) and *params*
            is a list of bind values.
    """
    where_clause = ""
    params = []
    if category:
        where_clause = " WHERE category = ?"
        params.append(category)
    return where_clause, params


def get_all_posts(category=None, page=None, per_page=5):
    """Retrieve posts with optional category filter and pagination.

    When *page* is ``None``, returns a plain list of all matching
    posts (backwards-compatible). When *page* is an integer, returns
    a dict containing the paginated posts and metadata.

    Args:
        category (str, optional): Filter by category name.
        page (int, optional): The 1-based page number.
        per_page (int): Number of posts per page. Defaults to 5.

    Returns:
        list or dict: A list of ``sqlite3.Row`` when *page* is None,
            or a dict with keys ``posts``, ``page``, ``total_pages``,
            and ``total`` when paginating.
    """
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
    """Search posts by title or content using SQL LIKE.

    Args:
        query (str): The search keyword.

    Returns:
        list: A list of ``sqlite3.Row`` matching the query,
            ordered by creation date descending.
    """
    db = get_db()
    posts = db.execute(
        "SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC",
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    return posts


def get_post(post_id):
    """Retrieve a single post by its ID.

    Args:
        post_id (int): The primary key of the post.

    Returns:
        sqlite3.Row or None: The matching post, or ``None`` if not found.
    """
    db = get_db()
    return db.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()


def create_post(title, content, category='general'):
    """Insert a new post into the database.

    Args:
        title (str): The post title.
        content (str): The post body text.
        category (str): The category name. Defaults to ``'general'``.
    """
    db = get_db()
    db.execute(
        "INSERT INTO posts (title, content, category) VALUES (?, ?, ?)",
        (title, content, category)
    )
    db.commit()


def update_post(post_id, title, content, category):
    """Update an existing post.

    Args:
        post_id (int): The primary key of the post to update.
        title (str): The new title.
        content (str): The new body text.
        category (str): The new category.
    """
    db = get_db()
    db.execute(
        "UPDATE posts SET title = ?, content = ?, category = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (title, content, category, post_id)
    )
    db.commit()


def delete_post(post_id):
    """Delete a post by its ID.

    Args:
        post_id (int): The primary key of the post to delete.
    """
    db = get_db()
    db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    db.commit()


def get_stats():
    """Compute aggregate statistics for all posts.

    Returns:
        dict: A dict with keys ``total`` (int), ``by_category``
            (list of rows with category and count), and ``by_month``
            (list of rows with month and count).
    """
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
