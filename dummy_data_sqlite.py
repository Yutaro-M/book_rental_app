from db_con import get_connection
import sqlite3
from faker import Factory

fake = Factory.create('ja_JP')

con = get_connection()
cur = con.cursor()
try:
    for _ in range(30):
        cur.execute('''
            INSERT INTO books (isbn, title, author, person, publisher, pubdate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [fake.random_number(digits=13, fix_len=True), '書籍:'+fake.town(), fake.name(), 'faker', fake.company(), fake.date() ])
    con.commit()
except sqlite3.IntegrityError as e:
    print(f'エラー内容: {e}')
    con.rollback()
finally:
    cur.close()
    con.close()
