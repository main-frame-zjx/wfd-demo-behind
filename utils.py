from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

def generate_token(user_id):
    return serializer.dumps(user_id, salt='auth')

def verify_token(token, max_age=86400): # 从7200改为86400（24小时）
    try:
        user_id = serializer.loads(token, salt='auth', max_age=max_age)
        return user_id
    except:
        return None

def hash_password(password):
    return generate_password_hash(password)

def check_password(password_hash, password):
    return check_password_hash(password_hash, password)