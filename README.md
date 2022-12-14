# URL
https://flask-book-rental.herokuapp.com/

# 概要
書籍やユーザーの登録を行い、書籍の貸し出しを管理するためのシステム

# 機能
- 書籍の登録：ISBNを入力すると書籍情報の一覧が表示され、書籍を登録できる
- ユーザーの登録：ユーザーの名前やメールアドレスなどを登録できる
- 書籍/ユーザーの削除：不要になった書籍やユーザーの情報を削除できる
- 貸し出し管理：書籍とユーザーを入力することで、貸し出しの登録/返却できる
- ログイン機能
- ページネーション機能

# 使用した技術
- フレームワークにPythonのFlaskを使用
- データベースにPostgreSQLを使用（当初はSQLiteを使用していたが、Herokuにデプロイするために移行）
- PostgreSQLに接続するためのライブラリにpg8000を使用
- Flaskのブループリントを使ったファイルの分割
- ISBNを入力した際に、非同期処理（Fetch）を利用して書籍情報を取得
- DOM操作のイベントリスナを利用して、ISBNの文字数が規定の数を超えたときにAPIを取得する関数を実行
- Heroku Postgres（アドオン）を利用したデータベースの接続
- プレースホルダを使用したSQLインジェクション対策
- バッシュ関数にSHA-256を使用し、パスワードをハッシュ化

# ログインIDとパスワード
- ログインIDは「a」、パスワードは「b」でログイン可能（入力欄に記載をしている）
