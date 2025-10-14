from flask_mysqldb import MySQL
import uuid
import os
from config import Config
from dataclasses import dataclass
from datetime import datetime  # 新增导入

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
    # add a user
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
    def get_by_id(id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, username, password_hash, status, role FROM users WHERE id = %s', (id,))
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

    @staticmethod
    def get_role_by_id(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('''
                    SELECT role FROM users 
                    WHERE id = %s AND status = 0
                ''', (user_id,))
        user = cursor.fetchone()
        return user


@dataclass
class FileInfo:
    id: int
    filename: str
    filepath: str
    uploaded_at: datetime

class File:


    @staticmethod
    def save_file(user_id, filename, filepath):
        """保存用户文件记录到数据库"""
        cursor = mysql.connection.cursor()

        # Step1: 检查文件名冲突
        cursor.execute('''
            SELECT filename FROM files 
            WHERE user_id = %s AND filename = %s
        ''', (user_id, filename))
        if cursor.fetchone():
            raise ValueError(f"文件 '{filename}' 已存在")

        uploaded_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 格式化为MySQL可识别的字符串

        # Step2: 插入新记录
        cursor.execute('''
            INSERT INTO files (user_id, filename, filepath, uploaded_at)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, filename, filepath, uploaded_at))
        mysql.connection.commit()
        return True

    @staticmethod
    def overwrite_file(user_id, filename, filepath):
        cursor = mysql.connection.cursor()
        try:
            # Step1: 检查记录是否存在
            cursor.execute('''
                        SELECT id, filepath FROM files 
                        WHERE user_id = %s AND filename = %s
                    ''', (user_id, filename))
            existing_file = cursor.fetchone()

            if not existing_file:
                raise FileNotFoundError(f"文件 '{filename}' 不存在")

            old_filepath = existing_file[1]  # 获取旧文件路径
            uploaded_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 更新时间戳

            # Step2: 更新记录
            cursor.execute('''
                        UPDATE files 
                        SET filepath = %s, uploaded_at = %s 
                        WHERE id = %s
                    ''', (filepath, uploaded_at, existing_file[0]))
            mysql.connection.commit()

            # Step3: 删除旧文件
            # try:
            #     if os.path.exists(old_filepath):
            #         os.remove(old_filepath)  # 删除旧文件释放空间
            # except Exception as e:
            #     print(f"删除旧文件失败: {e}")  # 日志记录但不中断流程

            return True
        except Exception as e:
            mysql.connection.rollback()
            print(f"覆盖文件失败: {e}")
            raise

    @staticmethod
    def delete_file(user_id, filename):
        """删除用户文件记录及物理文件"""
        cursor = mysql.connection.cursor()

        # Step1: 检查文件是否存在
        cursor.execute('''
                SELECT filepath FROM files 
                WHERE user_id = %s AND filename = %s
            ''', (user_id, filename))
        file_record = cursor.fetchone()
        if not file_record:
            raise FileNotFoundError(f"文件 '{filename}' 不存在")

        # Step2: 从数据库删除记录
        cursor.execute('''
                DELETE FROM files 
                WHERE user_id = %s AND filename = %s
            ''', (user_id, filename))
        mysql.connection.commit()

        # Step3: 删除物理文件
        file_path = file_record[0]
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"删除文件失败: {e}")
            raise RuntimeError("文件删除异常，请检查服务器权限")

    @staticmethod
    def get_user_files(user_id):
        """获取用户所有文件信息"""
        cursor = mysql.connection.cursor()
        cursor.execute('''
                SELECT id, filename, filepath, uploaded_at FROM files 
                WHERE user_id = %s
            ''', (user_id,))
        return [FileInfo(*row) for row in cursor.fetchall()]

    @staticmethod
    def get_user_file(user_id, filename):
        """获取用户所有文件信息"""
        cursor = mysql.connection.cursor()
        cursor.execute('''
                    SELECT id, filepath, uploaded_at FROM files 
                    WHERE user_id = %s AND filename = %s
                ''', (user_id,filename))
        return cursor.fetchone()[1]



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

    @staticmethod
    def get_by_reg_id(reg_id):
        # 获取注册请求详情
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register_tables WHERE id = %s', (reg_id,))
        reg = cursor.fetchone()
        return reg

    @staticmethod
    def approve_register(reg_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM register_tables WHERE id = %s', (reg_id,))
        reg = cursor.fetchone()
        # 创建用户
        cursor.execute('''
                INSERT INTO users 
                (username, password_hash, note, role)
                VALUES (%s, %s, %s, 'user')
            ''', (reg[1], reg[2], reg[3]))

        # 更新注册状态
        cursor.execute('''
                UPDATE register_tables 
                SET approve = 1 
                WHERE id = %s
            ''', (reg_id,))
        mysql.connection.commit()
        return reg