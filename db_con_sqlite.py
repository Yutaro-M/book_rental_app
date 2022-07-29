# コネクションオブジェクトを取得する部分をモジュール化

import sqlite3
from pathlib import Path

def get_connection():
    '''
    情報を登録する画面を表示

    Parameters:
    -----------
    なし

    Return:
    -------
    テンプレート文字列
    '''
    '''
    指定のデータベースに接続します。

    引数:
    -----
    なし

    戻り値
    -----
    DB接続済みのConnectionオブジェクト
    '''
    dir_exe = Path(__file__).parent.resolve()
    dbname = 'book_rental.db'
    fullpath = dir_exe.joinpath(dbname)
    con = sqlite3.connect(fullpath)
    con.row_factory = sqlite3.Row
    return con
