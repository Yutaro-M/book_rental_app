from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import request
from flask import session
from db_con import get_connection

# ブループリントオブジェクトの作成
rental_obj = Blueprint('rental_bp', __name__)

# 情報を登録する画面を表示
@rental_obj.route('/reg-rental')
def reg_rental():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'reg-rental': 'active'}
    return render_template('reg-rental.html', message=message, navigation=navigation)

# 入力した情報をDBに登録
@rental_obj.route('/reg-rental-db', methods=['POST'])
def reg_rental_db():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'reg-rental': 'active'}
    user_id = request.form.get('user_id')
    book_id = request.form.get('book_id')

    # ユーザーIDが空文字/空白の場合にエラーを発生
    if user_id.strip() == '':
        message['status'] = 'error'
        message['body'] = 'ユーザーIDが未入力です'
        return render_template('reg-rental.html', message = message, navigation=navigation)

    # 書籍IDが空文字/空白の場合にエラーを発生
    if book_id.strip() == '':
        message['status'] = 'error'
        message['body'] = '書籍IDが未入力です'
        return render_template('reg-rental.html', message = message, navigation=navigation)

    # ユーザーID/書籍IDが存在しない場合にエラーを表示
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT user_id
        FROM users
        WHERE user_id=?
    ''', [user_id])
    user_data = cur.fetchall();
    cur.execute('''
        SELECT id
        FROM books
        WHERE id=?
    ''', [book_id])
    book_data = cur.fetchall();
    cur.close()
    con.close()
    if not user_data:
        message['status'] = 'error'
        message['body'] = 'ユーザーIDが存在しません'
        return render_template('reg-rental.html', message = message, navigation=navigation)
    if not book_data:
        message['status'] = 'error'
        message['body'] = '書籍IDが存在しません'
        return render_template('reg-rental.html', message = message, navigation=navigation)

    # ユーザーID/書籍IDの組み合わせがすでに登録されていて、返却されていない場合、エラーを表示
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT *
        FROM rental
        WHERE user_id=? AND book_id=? AND returned_at is NULL
    ''', [user_id, book_id])
    user_book_data = cur.fetchall();
    cur.close()
    con.close()
    if user_book_data:
        message['status'] = 'error'
        message['body'] = '入力したユーザーは、現在書籍を借りています'
        return render_template('reg-rental.html', message = message, navigation=navigation)

    # 入力したユーザーIDと書籍IDを登録
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO rental (user_id, book_id, person_rental)
            VALUES (?, ?, ?)
        ''', [user_id, book_id, session['member_name']])
        con.commit()
        message['status'] = 'success'
        message['body'] = '登録完了しました'
    except Exception as e:
        print(f'エラー内容: {e}')
        message['status'] = 'error'
        message['body'] = 'エラーが発生しました'
        con.rollback()
    finally:
        cur.close()
        con.close()
    return render_template('reg-rental.html', message = message, navigation=navigation)

# DBの情報を取得して、表示
@rental_obj.route('/list-rental')
def list_rental():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'list-rental': 'active'}

    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT rental.user_id, user_name, book_id, title, substr(rental.created_at, 0, 11) AS created_at, substr(rental.returned_at, 0, 11) AS returned_at
        FROM rental
        INNER JOIN users
        ON rental.user_id = users.user_id
        INNER JOIN books
        ON rental.book_id = books.id
        ORDER BY returned_at DESC NULLS FIRST
    ''')
    rental_lst = cur.fetchall()
    cur.close()
    con.close()

    # DBの情報が格納されたリストを送る
    return render_template('list-rental.html',
        rental_lst = rental_lst,
        message = message, navigation=navigation)

# DBの内容を更新：「返却日」に日時を格納する
@rental_obj.route('/return-rental', methods=['POST'])
def return_rental():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'list-rental': 'active'}

    # ユーザーIDに対応して、返却日に日時を格納する
    user_book_lst = [None, None]
    if return_user_book_id := request.form.get('return-user-book-id'):
        # 「ユーザーID/書籍ID」とデータが送られてくるので、それを分割する
        user_book_lst = return_user_book_id.split('/')
    elif return_user_id := request.form.get('return-user-id'):
        return_book_id = request.form.get('return-book-id')
        user_book_lst = [return_user_id, return_book_id]

    con = get_connection()
    cur = con.cursor()
    # cur.execute('''
    #     SELECT returned_at
    #     FROM rental
    #     WHERE user_id = ? AND book_id = ? AND returned_at IS NOT NULL
    # ''', [user_book_lst[0], user_book_lst[1]])
    # rental_lst = cur.fetchall()

    cur.execute('''
        UPDATE rental
        SET returned_at = DATETIME('now', 'localtime'), person_return = ?
        WHERE user_id = ? AND book_id = ? AND returned_at IS NULL
    ''', [session['member_name'], user_book_lst[0], user_book_lst[1]])
    rowcount = cur.rowcount  # 処理件数を格納


    # if rental_lst:
    #     message['status'] = 'error'
    #     message['body'] = '返却済です'
    #     con.rollback()
    if rowcount == 0 :
        # 入力したIDが存在しない場合
        message['status'] = 'error'
        message['body'] = '正しいIDが入力されていません'
        con.rollback()
    else:
        # データを更新した場合
        message['status'] = 'success'
        message['body'] = '返却が完了しました'
        con.commit()

    # 情報を表示
    cur.execute('''
        SELECT rental.user_id, user_name, book_id, title, substr(rental.created_at, 0, 11) AS created_at, substr(rental.returned_at, 0, 11) AS returned_at
        FROM rental
        INNER JOIN users
        ON rental.user_id = users.user_id
        INNER JOIN books
        ON rental.book_id = books.id
        ORDER BY returned_at DESC NULLS FIRST
    ''')
    rental_lst = cur.fetchall()
    cur.close()
    con.close()

    return render_template('list-rental.html',
        rental_lst = rental_lst,
        message = message, navigation=navigation)
