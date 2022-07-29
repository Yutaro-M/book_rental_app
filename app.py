from flask import Flask, render_template, redirect, url_for
from flask import request
from book import book_obj
from user import user_obj
from rental import rental_obj
from login import login_obj

app = Flask(__name__)

app.register_blueprint(login_obj)
app.register_blueprint(book_obj)
app.register_blueprint(user_obj)
app.register_blueprint(rental_obj)

# シークレットキー（セッション情報を作成するために必要）
app.secret_key = 'test'



# @app.route('/')
# def index():
#     return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
