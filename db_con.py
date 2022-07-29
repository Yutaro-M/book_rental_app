# pg8000を使った方法
import pg8000
import os
import re
import ssl

def get_connection():
    # プレースホルダに「?」を使うために必要な一行
    pg8000.paramstyle = 'qmark'
    sslContext = ssl.create_default_context()  # SSLの接続情報を作成
    sslContext.check_hostname = False   # ホスト名を検証しない
    sslContext.verify_mode = ssl.CERT_NONE  # 証明証の検証をしない → 自己署名証明証が使える

    # Herokuにデプロイをした際には、HerokuのPostgreSQLに接続し、
    # ローカルで実行する際には、ローカルのPostgreSQLに接続する方法
    # os.environ()：キーが存在しない場合に、KeyError例外を投げる
    # os.getenv()：キーが存在しない場合に、Noneを返す
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        tpl = re.findall(r'postgres://(.*):(.*)@(.*):(.*)/(.*)', db_url)[0]
        con = pg8000.connect(
            user = tpl[0],
            password = tpl[1],
            host = tpl[2],
            port = tpl[3],
            database = tpl[4],
            ssl_context=sslContext
        )
    else:
        con = pg8000.connect(
        host='', port='', database='',
        user='', password='')

    return con


if __name__ == '__main__':
    conn = get_connection()
    conn.close()
