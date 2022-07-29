# データベースの作成（PostgreSQL）

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
        id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        isbn character varying,
        title character varying NOT NULL,
        author character varying,
        publisher character varying,
        pubdate character varying,
        person character varying,
        created_at timestamp without time zone DEFAULT now(),
        updated_at timestamp without time zone,
        deleted_at timestamp without time zone
        )
    ''')

    # ユーザーのテーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users(
        id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        user_id character varying NOT NULL UNIQUE,
        user_name character varying NOT NULL,
        user_email character varying,
        person character varying,
        created_at timestamp without time zone DEFAULT now(),
        updated_at timestamp without time zone
        )
    ''')

    # スタッフのテーブル（中身はDBから直接入力）
    cur.execute('''
        CREATE TABLE IF NOT EXISTS members(
        id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        member_id character varying NOT NULL UNIQUE,
        member_pwd character varying NOT NULL,
        member_name character varying NOT NULL,
        created_at timestamp without time zone DEFAULT now(),
        updated_at timestamp without time zone
        )
    ''')

    # 貸出管理のテーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rental(
        id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        user_id character varying NOT NULL,
        book_id INT NOT NULL,
        returned_at timestamp without time zone,
        person_rental character varying,
        person_return character varying,
        created_at timestamp without time zone DEFAULT now(),
        updated_at timestamp without time zone
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
