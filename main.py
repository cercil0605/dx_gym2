from project import create_app, db

# アプリケーションを作成
app = create_app()

# データベースの初期化
with app.app_context():
    db.create_all()  # データベースを作成（テーブルの作成）

if __name__ == '__main__':
    app.run(debug=True)
