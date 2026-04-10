"""Flask Blog application.

Defines routes for blog post CRUD, search, pagination,
statistics, and form validation.
"""

from flask import Flask, render_template, request, redirect, url_for, abort
from flasgger import Swagger

from models import (
    init_db, get_all_posts, get_post,
    create_post, update_post, delete_post, get_stats,
    search_posts
)

app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'
app.config['TESTING'] = False

swagger_template = {
    "info": {
        "title": "Flask Blog API",
        "description": "Flask 블로그 REST API 문서",
        "version": "2.0.0",
    }
}
Swagger(app, template=swagger_template)

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
    """Render the post list page with category filter and pagination.
    ---
    tags:
      - Posts
    parameters:
      - name: category
        in: query
        type: string
        required: false
        description: 필터링할 카테고리
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: 페이지 번호
    responses:
      200:
        description: 글 목록 HTML 페이지
    """
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
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: 조회할 글의 ID
    responses:
      200:
        description: 글 상세 HTML 페이지
      404:
        description: 글을 찾을 수 없음
    """
    post = get_post(post_id)
    if post is None:
        abort(404)
    return render_template('post.html', post=post)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Show the post creation form or process a new post.
    ---
    tags:
      - Posts
    parameters:
      - name: title
        in: formData
        type: string
        required: true
        description: 글 제목
      - name: content
        in: formData
        type: string
        required: true
        description: 글 내용
      - name: category
        in: formData
        type: string
        required: false
        default: general
        description: 카테고리
    responses:
      200:
        description: 작성 폼 또는 유효성 검사 오류
      302:
        description: 성공 시 글 목록으로 리다이렉트
    """
    if request.method == 'POST':
        title, content, category, error = validate_post_form(request.form)
        if error:
            return render_template('form.html', error=error)
        create_post(title, content, category)
        return redirect(url_for('index'))
    return render_template('form.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    """Show the post edit form or update the post.
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: 수정할 글의 ID
      - name: title
        in: formData
        type: string
        required: true
        description: 글 제목
      - name: content
        in: formData
        type: string
        required: true
        description: 글 내용
      - name: category
        in: formData
        type: string
        required: false
        default: general
        description: 카테고리
    responses:
      200:
        description: 수정 폼 또는 유효성 검사 오류
      302:
        description: 성공 시 글 목록으로 리다이렉트
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
    ---
    tags:
      - Posts
    parameters:
      - name: post_id
        in: path
        type: integer
        required: true
        description: 삭제할 글의 ID
    responses:
      302:
        description: 삭제 후 글 목록으로 리다이렉트
    """
    delete_post(post_id)
    return redirect(url_for('index'))


@app.route('/search')
def search():
    """Search posts by keyword and display results.
    ---
    tags:
      - Search
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: 검색 키워드
    responses:
      200:
        description: 검색 결과 HTML 페이지
      302:
        description: 빈 검색어 시 목록으로 리다이렉트
    """
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    posts = search_posts(query)
    return render_template('search.html', posts=posts, query=query)


@app.route('/stats')
def stats():
    """Render the statistics dashboard page.
    ---
    tags:
      - Stats
    responses:
      200:
        description: 통계 대시보드 HTML 페이지
    """
    stats_data = get_stats()
    return render_template('stats.html', stats=stats_data)


if __name__ == '__main__':
    app.run(debug=True)
