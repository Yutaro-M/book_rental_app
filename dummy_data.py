# pg8000を使った方法（プレースホルダに「?」を使えるので、sqliteと同じ書き方でよい）
from db_con import get_connection
from faker import Factory

fake = Factory.create('ja_JP')

con = get_connection()
cur = con.cursor()
try:
    for _ in range(80):
        cur.execute('''
            INSERT INTO books (isbn, title, author, person, publisher, pubdate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [fake.random_number(digits=13, fix_len=True), '書籍:'+fake.town(), fake.name(), 'faker', fake.company(), fake.date()])
    con.commit()
except Exception as e:
    print(f'エラー内容: {e}')
    con.rollback()
finally:
    cur.close()
    con.close()


# psycopg2を使った方法（プレースホルダに「?」を使えない、「%s」を使う）
"""
from db_con import get_connection
import psycopg2
from faker import Factory

fake = Factory.create('ja_JP')

con = get_connection()
con.set_client_encoding('UTF8')  # この一文はなくてもよい
cur = con.cursor()
try:
    for _ in range(1):
        cur.execute('''
            INSERT INTO books (isbn, title, author, person, publisher, pubdate)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', [fake.random_number(digits=13, fix_len=True), '書籍:'+fake.town(), fake.name(), 'faker', fake.company(), fake.date() ])
    con.commit()
except psycopg2.OperationalError as e:
    print(f'エラー内容: {e}')
    con.rollback()
finally:
    cur.close()
    con.close()
"""
