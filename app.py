"""Flask Blog application.

Defines routes for blog post CRUD, search, pagination,
statistics, and form validation.
"""

from flask import Flask, render_template, request, redirect, url_for, abort

from models import (
    init_db, get_all_posts, get_post,
    create_post, update_post, delete_post, get_stats,
    search_posts
)

app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'
app.config['TESTING'] = False

init_db(app)


def validate_post_form(form):
    """Validate the post creation/edit form fields.

    Extracts title, content, and category from the submitted form.
    Returns an error message if title or content is blank or
    whitespace-only.

    Args:
        form: A Flask ``ImmutableMultiDict`` from ``request.form``.

    Returns:
        tuple: ``(title, content, category, error)`` where *error*
            is ``None`` on success, or a Korean message string
            if validation fails.
    """
    title = form['title']
    content = form['content']
    category = form.get('category', 'general')
    if not title.strip() or not content.strip():
        return None, None, None, "제목과 내용을 입력해주세요"
    return title, content, category, None


@app.route('/')
def index():
    """Render the post list page with category filter and pagination."""
    category = request.args.get('category')
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    result = get_all_posts(category, page=page)
    return render_template('index.html',
                           posts=result['posts'],
                           category=category,
                           pagination=result)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    """Render the detail page for a single post.

    Args:
        post_id (int): The ID of the post to display.

    Returns:
        str: Rendered post.html template, or 404 if not found.
    """
    post = get_post(post_id)
    if post is None:
        abort(404)
    return render_template('post.html', post=post)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Show the post creation form (GET) or process a new post (POST)."""
    if request.method == 'POST':
        title, content, category, error = validate_post_form(request.form)
        if error:
            return render_template('form.html', error=error)
        create_post(title, content, category)
        return redirect(url_for('index'))
    return render_template('form.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    """Show the post edit form (GET) or update the post (POST).

    Args:
        post_id (int): The ID of the post to edit.
    """
    post = get_post(post_id)
    if request.method == 'POST':
        title, content, category, error = validate_post_form(request.form)
        if error:
            return render_template('form.html', post=post, error=error)
        update_post(post_id, title, content, category)
        return redirect(url_for('index'))
    return render_template('form.html', post=post)


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    """Delete a post and redirect to the index page.

    Args:
        post_id (int): The ID of the post to delete.
    """
    delete_post(post_id)
    return redirect(url_for('index'))


@app.route('/search')
def search():
    """Search posts by keyword and display results."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    posts = search_posts(query)
    return render_template('search.html', posts=posts, query=query)


@app.route('/stats')
def stats():
    """Render the statistics dashboard page."""
    stats_data = get_stats()
    return render_template('stats.html', stats=stats_data)


if __name__ == '__main__':
    app.run(debug=True)
