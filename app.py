from flask import Flask, render_template, request

from models import init_db, get_all_posts

app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'
app.config['TESTING'] = False

init_db(app)


@app.route('/')
def index():
    category = request.args.get('category')
    posts = get_all_posts(category)
    return render_template('index.html', posts=posts, category=category)


if __name__ == '__main__':
    app.run(debug=True)
