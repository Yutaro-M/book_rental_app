from email.mime import image
from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import request
from flask import session
from db_con import get_connection
import hashlib

# ブループリントオブジェクトの作成
login_obj = Blueprint('login_bp', __name__)

# シークレットキー（セッション情報を作成するために必要）
login_obj.secret_key = 'test'

# ログイン情報を入力
@login_obj.route('/')
def login():
    message = {}
    navigation = {}
    return render_template('login.html', message=message, navigation=navigation)

# ログイン情報を確認
@login_obj.route('/try-login', methods=['POST'])
def try_login():
    message = {}
    navigation = {}
    try_login_id = request.form.get('login-id')
    try_login_pwd = request.form.get('login-pwd')
    # パスワードをハッシュ化
    salt = 'ソルト'  # 本来はランダムな文字列
    data = try_login_pwd + salt
    binary = data.encode('utf-8')
    hash_value = hashlib.sha256(binary).hexdigest()
    for _ in range(10000):
        binary = hash_value.encode('utf-8')
        hash_value = hashlib.sha256(binary).hexdigest()

    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT member_id, member_pwd, member_name
        FROM members
        WHERE member_id=? AND member_pwd=?
    ''', [try_login_id, hash_value])
    member_data = cur.fetchall();  # IDとパスワードが一致しない場合、[]が取得される
    # pg8000を使用して、カラム名でアクセスするために必要な2行
    keys = [k[0] for k in cur.description]
    member_data = [dict(zip(keys, row)) for row in member_data]
    cur.close()
    con.close()
    print(member_data)
    # IDとパスワードが一致した場合に、セッション情報を作成する
    if member_data:
        session['login_session'] = True
        session['member_name'] = member_data[0]['member_name']
        return render_template('layout.html', navigation=navigation)
    else:
        message['status'] = 'error'
        message['body'] = 'ID/パスワードが一致しません'
        return render_template('login.html', message=message, navigation=navigation)

# ログアウト
@login_obj.route('/logout')
def logout():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    session.pop('login_session', None)
    session.pop('member_name', None)
    message['status'] = 'success'
    message['body'] = 'ログアウトしました'
    return render_template('login.html', message=message, navigation=navigation)


# ログイン情報を確認（DBを使わないパターンでボツ）
# DBを使用しないと、ログインした人の名前などを関連付けられない
"""
@login_obj.route('/try-login', methods=['POST'])
def try_login():
    # ログイン用のidとパスワード
    login_id_psw = {'a': 'b'}

    try_login_id = request.form.get('login-id')
    try_login_pwd = request.form.get('login-pwd')
    if try_login_id not in login_id_psw:
        print('idが正しくありません')
        return 'idが正しくありません'
    if try_login_pwd != login_id_psw[try_login_id]:
        print('パスワードが正しくありません')
        return 'パスワードが正しくありません'
    # idとパスワードが正しいとき、セッション情報を取得
    session['login_session'] = True
    return render_template('layout.html')
"""
