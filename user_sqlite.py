from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import request
from flask import session
from db_con import get_connection

# ブループリントオブジェクトの作成
user_obj = Blueprint('user_bp', __name__)

# 情報を登録する画面を表示
@user_obj.route('/reg-user')
def reg_user():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'reg-user': 'active'}
    return render_template('reg-user.html', message=message, navigation=navigation)

# 入力した情報をDBに登録
@user_obj.route('/reg-user-db', methods=['POST'])
def reg_user_db():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'reg-user': 'active'}
    user_id = request.form.get('user_id')
    user_name = request.form.get('user_name')
    user_email = request.form.get('user_email')

    # ユーザーIDが重複した場合にエラーを発生
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT COUNT(*) AS user_id_cnt
        FROM users
        WHERE user_id = ?
    ''', [user_id])
    user_id_num = cur.fetchall()
    if int(user_id_num[0]['user_id_cnt']) >= 1:
        message['status'] = 'error'
        message['body'] = "入力したIDは登録済です"
        return render_template('reg-user.html', message = message, navigation=navigation)

    # ユーザーIDが空文字/空白の場合にエラーを発生
    if user_id.strip() == '':
        message['status'] = 'error'
        message['body'] = "IDが未入力です"
        return render_template('reg-user.html', message = message, navigation=navigation)

    # 名前が空文字/空白の場合にエラーを発生
    if user_name.strip() == '':
        message['status'] = 'error'
        message['body'] = "氏名が未入力です"
        return render_template('reg-user.html', message = message, navigation=navigation)

    # 入力したユーザーデータを登録
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO users (user_id, user_name, user_email, person)
            VALUES (?, ?, ?, ?)
        ''', [user_id, user_name, user_email, session['member_name']])
        con.commit()
        message['status'] = 'success'
        message['body'] = "登録完了しました。"
    except Exception as e:
        print(f'エラー内容: {e}')
        message['status'] = 'error'
        message['body'] = "エラーが発生しました"
        con.rollback()
    finally:
        cur.close()
        con.close()
    return render_template('reg-user.html', message = message, navigation=navigation)

# DBに入力した情報を確認
@user_obj.route('/list-user')
def list_user():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'list-user': 'active'}

    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT user_id, user_name, user_email, person, substr(created_at, 0, 11) AS created_at, updated_at
        FROM users
        ORDER BY created_at DESC
    ''')
    user_lst = cur.fetchall()
    cur.close()
    con.close()

    # DBの情報が格納されたリストを送る
    return render_template('list-user.html',
        user_lst = user_lst,
        message = message, navigation=navigation)

# DBの内容を削除（IDを記入して削除）
@user_obj.route('/delete-user', methods=['POST'])
def delete_user():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'list-user': 'active'}
    delete_user_id = request.form.get('delete-user-id')

    # idに対応するデータを削除
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        DELETE FROM users
        WHERE user_id = ?
    ''', [delete_user_id])
    print("処理件数"  , cur.rowcount)  # 処理件数の確認
    rowcount = cur.rowcount  # 処理件数を格納
    # delete文では存在しないidを入力してもエラーにならない
    # 削除された件数によって、メッセージを変える
    if rowcount == 0 :
        # 入力したidが存在しない場合
        message['status'] = 'error'
        message['body'] = "入力したidは存在しません"
        con.rollback()
    else:
        # データを削除した場合
        message['status'] = 'success'
        message['body'] = "データを削除しました"
        con.commit()

    # 書籍の情報を表示
    cur.execute('''
        SELECT user_id, user_name, user_email, person, substr(created_at, 0, 11) AS created_at, updated_at
        FROM users
        ORDER BY created_at DESC
    ''')
    user_lst = cur.fetchall()
    cur.close()
    con.close()

    return render_template('list-user.html',
        user_lst = user_lst,
        message = message, navigation=navigation)
