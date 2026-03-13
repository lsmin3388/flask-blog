from flask import Flask

from models import init_db

app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'
app.config['TESTING'] = False

init_db(app)

if __name__ == '__main__':
    app.run(debug=True)
