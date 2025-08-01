from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    @staticmethod
    def hash_password(password):
        """使用SHA-256加密密码（生产环境建议使用bcrypt）"""
        return generate_password_hash(password, method='sha256')
    
    @staticmethod
    def verify_password(password, hashed):
        """验证密码与哈希值是否匹配"""
        return check_password_hash(hashed, password)