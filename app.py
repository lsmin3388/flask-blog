from flask import Flask, render_template, request, redirect, url_for, abort

from models import (
    init_db, get_all_posts, get_post,
    create_post, update_post, delete_post, get_stats
)

app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'
app.config['TESTING'] = False

init_db(app)


@app.route('/')
def index():
    category = request.args.get('category')
    posts = get_all_posts(category)
    return render_template('index.html', posts=posts, category=category)


@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = get_post(post_id)
    if post is None:
        abort(404)
    return render_template('post.html', post=post)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'general')
        if not title.strip() or not content.strip():
            return render_template('form.html', error="제목과 내용을 입력해주세요")
        create_post(title, content, category)
        return redirect(url_for('index'))
    return render_template('form.html')


@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    post = get_post(post_id)
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form.get('category', 'general')
        if not title.strip() or not content.strip():
            return render_template('form.html', post=post, error="제목과 내용을 입력해주세요")
        update_post(post_id, title, content, category)
        return redirect(url_for('index'))
    return render_template('form.html', post=post)


@app.route('/delete/<int:post_id>', methods=['POST'])
def delete(post_id):
    delete_post(post_id)
    return redirect(url_for('index'))


@app.route('/stats')
def stats():
    stats_data = get_stats()
    return render_template('stats.html', stats=stats_data)


if __name__ == '__main__':
    app.run(debug=True)
