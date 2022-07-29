# データベースの作成：SQLite

from db_con import get_connection

def create_table():
    '''
    DBのテーブルを作成
    '''
    # ISBNは空文字の重複を許容したいので、UNIQUE制約を外した
    con = get_connection()
    cur = con.cursor()
    # 本のテーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT,
        title TEXT NOT NULL,
        author TEXT,
        publisher TEXT,
        pubdate TEXT,
        person TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT,
        deleted_at TEXT
        )
    ''')

    # ユーザーのテーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL UNIQUE,
        user_name TEXT NOT NULL,
        user_email TEXT,
        person TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT
        )
    ''')

    # スタッフのテーブル（中身はDBから直接入力）
    cur.execute('''
        CREATE TABLE IF NOT EXISTS members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INT NOT NULL UNIQUE,
        member_pwd TEXT NOT NULL,
        member_name TEXT NOT NULL,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT
        )
    ''')

    # 貸出管理のテーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rental(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        book_id INT NOT NULL,
        returned_at TEXT,
        person_rental TEXT,
        person_return TEXT,
        created_at TEXT DEFAULT (DATETIME('now', 'localtime')),
        updated_at TEXT
        )
    ''')
    con.commit()
    cur.close()
    con.close()

if __name__ == '__main__':
    create_table()
    print("テーブルが正常に作成されました。")
else:
    print("このファイルはimportしないでください")
    exit(1)
