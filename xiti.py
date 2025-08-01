from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

# 配置类定义
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'
    

app = Flask(__name__)
app.config.from_object(Config)  # 现在Config已定义
db = SQLAlchemy(app)



# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    height = db.Column(db.Float)  # 单位cm
    weight = db.Column(db.Float)  # 单位kg

    def set_password(self, password):
        self.password_hash = AuthService.hash_password(password)

    def check_password(self, password):
        return AuthService.verify_password(password, self.password_hash)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ['username', 'password']):
        return jsonify({"error": "缺少用户名或密码"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "用户名已存在"}), 409

    user = User(
        username=data['username'],
        height=float(data.get('height', 0)),
        weight=float(data.get('weight', 0))
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "注册成功", "user_id": user.id}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if not user or not user.check_password(data.get('password')):
        return jsonify({"error": "用户名或密码错误"}), 401

    bmi_data = BMIService.calculate_all(user.height, user.weight)
    return jsonify({
        "message": "登录成功",
        "user_id": user.id,
        "bmi": bmi_data
    })

@app.route('/bmi', methods=['POST'])
def calculate_bmi():
    data = request.get_json()
    height = float(data.get('height', 0))
    weight = float(data.get('weight', 0))
    return jsonify(BMIService.calculate_all(height, weight))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)