import os

class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306  # 端口号
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root1234'
    MYSQL_DB = 'dataflow'
    SECRET_KEY = 'your-secret-key-here'  # 生产环境应使用随机密钥
    UPLOAD_FOLDER = 'uploads'
    # 配置文件路径（添加到Config类）
    PUBLIC_FOLDER = os.path.join(os.path.dirname(__file__), 'public')