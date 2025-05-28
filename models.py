from flask_mysqldb import MySQL
import uuid
import os
from config import Config
from dataclasses import dataclass

mysql = MySQL()





def init_db(app):
    app.config['MYSQL_HOST'] = Config.MYSQL_HOST
    app.config['MYSQL_USER'] = Config.MYSQL_USER
    app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
    app.config['MYSQL_DB'] = Config.MYSQL_DB
    mysql.init_app(app)
    ensure_upload_dir(app)

def ensure_upload_dir(app):
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)

class User:
    # 用于直接添加用户，是一个后门
    @staticmethod
    def create(username, password_hash,role):
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash,role)
                VALUES (%s, %s, %s)
            ''', (username, password_hash,role))
            mysql.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    @staticmethod
    def get_by_username(username):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, username, password_hash, status, role FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        return user if user else None

    @staticmethod
    def get_all_user():
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, username,note, status, role FROM users')
        users = cursor.fetchall()
        return users if users else None

    @staticmethod
    def update_status(user_id, new_status):
        cursor = mysql.connection.cursor()
        cursor.execute('''
                UPDATE users 
                SET status = %s 
                WHERE id = %s
            ''', (new_status, user_id))
        mysql.connection.commit()

    @staticmethod
    def update_note(user_id, new_note):
        cursor = mysql.connection.cursor()
        cursor.execute('''
                UPDATE users 
                SET note = %s 
                WHERE id = %s
            ''', (new_note, user_id))
        mysql.connection.commit()


@dataclass
class FileInfo:
    id: int
    filename: str
    filepath: str

class File:
    @staticmethod
    def get_latest_user_file(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('''
                SELECT id, filename, filepath 
                FROM files 
                WHERE user_id = %s 
                ORDER BY id DESC 
                LIMIT 1
            ''', (user_id,))
        result = cursor.fetchone()
        return FileInfo(*result) if result else None

    @staticmethod
    def save_file(user_id, filename, filepath):
        cursor = mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO files (user_id, filename, filepath)
            VALUES (%s, %s, %s)
        ''', (user_id, filename, filepath))
        mysql.connection.commit()
        return cursor.lastrowid

    @staticmethod
    def get_user_file(user_id, file_id):
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT id, filename, filepath 
            FROM files 
            WHERE id = %s AND user_id = %s
        ''', (file_id, user_id))
        return cursor.fetchone()


class Register:
    @staticmethod
    def create(username, password_hash, note):
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO register_tables 
                (username, password_hash, note)
                VALUES (%s, %s, %s)
            ''', (username, password_hash, note))
            mysql.connection.commit()
            return True
        except Exception as e:
            print(f"注册请求失败: {e}")
            return False

    @staticmethod
    def get_by_approve(approve_status):
        cursor = mysql.connection.cursor()
        cursor.execute('''
            SELECT id, username, note 
            FROM register_tables 
            WHERE approve = %s
        ''', (approve_status,))
        return cursor.fetchall()