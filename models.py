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
    @staticmethod
    def create(username, password_hash):
        cursor = mysql.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
            ''', (username, password_hash))
            mysql.connection.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False

    @staticmethod
    def get_by_username(username):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        return user if user else None


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