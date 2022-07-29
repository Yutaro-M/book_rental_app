from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import request
from flask import session
import sqlite3
from db_con import get_connection

from flask_paginate import Pagination, get_page_parameter

# ブループリントオブジェクトの作成
book_obj = Blueprint('book_bp', __name__)

# 情報を登録する画面を表示
@book_obj.route('/reg-book')
def reg_book():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'reg-book': 'active'}
    # navigation = {'reg-user': '', 'list-user': '', 'reg-book': 'active', 'list-book': ''}
    # と記述しなければならない言語も存在する（キーが存在しないとエラーになるから）
    # Flask（テンプレートエンジンのJinja）では、キーが存在しない場合にエラーにならない
    return render_template('reg-book.html', message=message, navigation=navigation)

# 入力した情報をDBに登録
@book_obj.route('/reg-book-db', methods=['POST'])
def reg_book_db():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'reg-book': 'active'}

    isbn = request.form.get('isbn')
    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    pubdate = request.form.get('pubdate')

    # ISBNの重複、タイトルの重複と空文字/空白をチェック
    # ISBNの件数を取得
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        SELECT COUNT(*) AS isbn_cnt
        FROM books
        WHERE isbn = ?
    ''', [isbn])
    isbn_num = cur.fetchall()
    # pg8000を使用して、カラム名でアクセスするために必要な2行
    keys = [k[0] for k in cur.description]
    isbn_num = [dict(zip(keys, row)) for row in isbn_num]
    print('件数', isbn_num[0]['isbn_cnt'])  # print('件数', isbn_num[0][0])

    # ISBNが空文字ではない and 重複した場合にエラーを発生
    if isbn != '' and int(isbn_num[0]['isbn_cnt']) >= 1:  # if isbn != '' and int(isbn_num[0][0]) >= 1:
        message['status'] = 'error'
        message['body'] = '入力したISBNは登録済です'
        return render_template('reg-book.html', message = message, navigation=navigation)
    # タイトルが空文字/空白の場合にエラーを発生
    if title.strip() == '':
        message['status'] = 'error'
        message['body'] = 'タイトルが未入力です'
        return render_template('reg-book.html', message = message, navigation=navigation)
    # 発売日が空白のとき、空文字をNoneに変換（PostgreSQLの日付型には空文字を入れられない）
    if pubdate == '':
        pubdate = None
    """ 当初はタイトルの重複を禁止していて、その時のコード
    # タイトルの件数を取得
    cur.execute('''
        SELECT COUNT(*) AS title_cnt
        FROM books
        WHERE title = ?
    ''', [title])
    title_num = cur.fetchall()
    print('件数', title_num[0]['title_cnt'])
    cur.close()
    con.close()
    elif int(title_num[0]['title_cnt']) >= 1:
        message['status'] = 'error'
        message['body'] = "タイトルが重複しています"
        return render_template('reg-book.html', message = message)
    """

    # 入力した書籍データを登録
    """
    現在のコードでは、try/exept/finallyの例外処理は不要。
    当初はISBNのカラムにUNIQUE制約を付けていたが、
    その際のエラー処理の方法が参考になるので、残している。
    """
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute('''
            INSERT INTO books (isbn, title, author, person, publisher, pubdate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [isbn, title, author, session['member_name'], publisher, pubdate])
        con.commit()
        message['status'] = 'success'
        message['body'] = "登録完了しました"
    except sqlite3.IntegrityError  as e:
        print(f'エラー内容: {e}')
        message['status'] = 'error'
        message['body'] = "入力したISBNは登録済です（try/exept/finally）"
        con.rollback()
    # エラーをすべて補足する場合
    # except Exception  as e:
    #     if e.args[0].startswith('UNIQUE'):
    #         message['status'] = 'error'
    #         message['body'] = "書籍データが重複しています。"
    #         con.rollback()
    finally:
        cur.close()
        con.close()
    return render_template('reg-book.html', message = message, navigation=navigation)

# DBに入力した情報を確認
@book_obj.route('/list-book')
def list_book():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'list-book': 'active'}

    # ページ番号がGETで送られてくる
    page = request.args.get('page')
    if page is None:
        page = 1
    else:
        page  = int(page)

    con = get_connection()
    cur = con.cursor()
    # DBの情報を表示
    cur.execute('''
        SELECT id, isbn, title, author, publisher, pubdate, person, to_char(created_at, 'yyyy-mm-dd') as created_at, updated_at
        FROM books
        WHERE deleted_at is NULL
        ORDER BY created_at DESC
        LIMIT 20 OFFSET ?
    ''',[(page - 1) * 20])
    book_lst = cur.fetchall()  # book_lst = [i for i in cur] と意味は同じ
    # pg8000を使用して、カラム名でアクセスするために必要な2行
    keys = [k[0] for k in cur.description]
    book_lst = [dict(zip(keys, row)) for row in book_lst]
    # レコードの数を取得（ページネーションで使用）
    cur.execute('''
    SELECT COUNT(*) AS record_cnt
    FROM books
    WHERE deleted_at is NULL
    ''')
    record_data = cur.fetchall()
    # pg8000を使用して、カラム名でアクセスするために必要な2行
    keys = [k[0] for k in cur.description]
    record_data = [dict(zip(keys, row)) for row in record_data]
    record_num = int(record_data[0]['record_cnt'])  # record_num = int(record_data[0][0])
    cur.close()
    con.close()
    # ページネーションの設定
    # page：現在のページ、total:レコードの全件数、per_page:1ページのレコードの表示件数
    # display_msg：HTMLで表示される内容、css_framework：CSSフレームワーク
    pagination = Pagination(page=page, total=record_num, per_page=20,
        display_msg = '<b>{total}</b> 件中、<b>{start} - {end}</b> 件を表示',
        css_framework='semantic'
    )
    # DBの情報が格納されたリストを送る
    return render_template('list-book.html',
        book_lst = book_lst,
        message = message, navigation=navigation,
        pagination = pagination
    )

# DBの内容を削除（IDを記入して削除）
@book_obj.route('/delete-book', methods=['POST', 'GET'])
def delete_book():
    message = {}
    navigation = {}
    if 'login_session' not in session:
        return render_template('login.html', message=message, navigation=navigation)
    navigation = {'list-book': 'active'}

    delete_book_id = request.form.get('delete-book-id')
    # idに対応するデータを削除
    con = get_connection()
    cur = con.cursor()
    # 論理削除（削除されていない場合、deleted_atがNULL）
    cur.execute('''
        UPDATE books
        SET deleted_at = now()
        WHERE id = ? AND deleted_at is NULL
    ''', [delete_book_id])

    # 物理削除をしていた時のコード
    # 削除済の書籍を貸出履歴を表示させるために、論理削除へ変更
    # cur.execute('''
    #     DELETE FROM books
    #     WHERE id = ?
    # ''', [delete_book_id])

    print("処理件数"  , cur.rowcount)  # 処理件数の確認
    rowcount = cur.rowcount  # 処理件数を格納
    # delete文では存在しないidを入力してもエラーにならない
    # 削除された件数によって、メッセージを変える
    if request.method == 'POST':
        if rowcount == 0 :
            # 入力したidが存在しない場合
            message['status'] = 'error'
            message['body'] = '入力したidは存在しません'
            con.rollback()
        else:
            # データを削除した場合
            message['status'] = 'success'
            message['body'] = 'データを削除しました'
            con.commit()

    # ページネーションの設定
    # ページを閲覧する場合（ページネーションのリンクを押す場合）、GETでページ情報が送られてくる → delete-book?page=2
    if request.method == 'GET':
        page = request.args.get('page')
        if page is None:
            page = 1
        else:
            page  = int(page)
    # レコードを削除した場合、そのときのページ情報がPOSTで送られてくる
    if request.method == 'POST':
        page = request.form.get('page-param')
        if not page:
            page = 1
        else:
            page  = int(page)

    # 書籍の情報を表示
    cur.execute('''
        SELECT id, isbn, title, author, publisher, pubdate, person, to_char(created_at, 'yyyy-mm-dd') as created_at, updated_at
        FROM books
        WHERE deleted_at is NULL
        ORDER BY created_at DESC
        LIMIT 20 OFFSET ?
    ''',[(page - 1) * 20])
    book_lst = cur.fetchall()
    # pg8000を使用して、カラム名でアクセスするために必要な2行
    keys = [k[0] for k in cur.description]
    book_lst = [dict(zip(keys, row)) for row in book_lst]

    # レコードの数を取得（ページネーションで使用）
    cur.execute('''
    SELECT COUNT(*) AS record_cnt
    FROM books
    WHERE deleted_at is NULL
    ''')
    record_data = cur.fetchall()
    # pg8000を使用して、カラム名でアクセスするために必要な2行
    keys = [k[0] for k in cur.description]
    record_data = [dict(zip(keys, row)) for row in record_data]
    record_num = int(record_data[0]['record_cnt'])  # record_num = int(record_data[0][0])
    cur.close()
    con.close()
    # ページネーションの設定
    pagination = Pagination(page=page, total=record_num, per_page=20,
        display_msg = '<b>{total}</b> 件中、<b>{start} - {end}</b> 件を表示',
        css_framework='semantic'
    )

    return render_template('list-book.html',
        book_lst = book_lst,
        message = message, navigation=navigation,
        pagination=pagination
    )
