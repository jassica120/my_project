from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv # 從 python-dotenv 套件中載入讀取 .env 檔的功能
import os   # 匯入 os 模組，用來讀取環境變數

# 載入 .env 檔案中的變數（例如 DB_URI），讓 os.getenv 可以取得它
load_dotenv()

app = Flask(__name__)

# PostgreSQL 資料庫連線字串格式：
# postgresql://使用者:密碼@主機:埠號/資料庫名稱
# 從環境變數中讀取名為 'DB_URI' 的值（也就是你的 PostgreSQL 連線字串），這樣就不會把密碼寫死在程式中
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)    # 建立資料庫實例（綁定到 Flask app）

# 建立資料模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)        # 使用者編號（主鍵，自動編號）
    username = db.Column(db.String(80), unique=True, nullable=False)    # 使用者名稱（唯一、必填
    email = db.Column(db.String(120), unique=True, nullable=False)      # 電子郵件（唯一、必填）

    # 用來顯示 User 物件時的文字描述
    def __repr__(self):
        return f'<User {self.username}>'

# 在應用程式上下文外部建立表格 (只在第一次運行或進行資料庫遷移時執行)
# 這將根據您的模型定義在 PostgreSQL 資料庫中建立 'users' 表格
with app.app_context():
    db.create_all()

# 首頁
@app.route('/')
def index():
    users = User.query.all() # 查詢所有用戶
    return render_template('index.html', users=users) # 渲染模板並傳遞數據

# 新增用戶資料
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
         # 從表單取得輸入的使用者名稱與 Email
        username = request.form['username']
        email = request.form['email']
        
        new_user = User(username=username, email=email)  # 建立一個新的使用者物件
        db.session.add(new_user) # 將新用戶添加到會話
        db.session.commit()      # 提交更改到資料庫
        return redirect(url_for('index'))
    return render_template('add_user.html')

# 刪除用戶資料
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # 根據 user_id 查詢要刪除的用戶
    user_to_delete = User.query.get_or_404(user_id)
    
    # 從資料庫會話中刪除用戶
    db.session.delete(user_to_delete)
    # 提交更改
    db.session.commit()
    
    # 刪除後重定向回首頁
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)



