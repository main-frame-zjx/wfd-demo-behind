from flask import Flask, request, jsonify, send_from_directory
from models import mysql, User, File, init_db
from utils import generate_token, verify_token, hash_password, check_password
from config import Config
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

from datetime import datetime
import json



app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
init_db(app)


@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    print('username',username)
    print('password',password)

    if User.get_by_username(username):
        return jsonify({'error': 'Username already exists'}), 400

    hashed_pw = hash_password(password)
    if User.create(username, hashed_pw):
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'error': 'User creation failed'}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    user = User.get_by_username(username)
    if user and check_password(user[2], password):
        token = generate_token(user[0])
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401


# @app.route('/upload', methods=['POST'])
# def upload_file():
#     token = request.form.get('token')
#     user_id = verify_token(token)
#     if not user_id:
#         return jsonify({'error': 'Invalid or expired token'}), 401
#
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'}), 400
#
#     filename = secure_filename(file.filename)
#     save_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
#     os.makedirs(save_dir, exist_ok=True)
#     filepath = os.path.join(save_dir, filename)
#     file.save(filepath)
#
#     File.save_file(user_id, filename, filepath)
#     return jsonify({'message': 'File uploaded successfully'}), 201
#
#
# @app.route('/download/<int:file_id>', methods=['GET'])
# def download_file(file_id):
#     token = request.args.get('token')
#     user_id = verify_token(token)
#     if not user_id:
#         return jsonify({'error': 'Invalid or expired token'}), 401
#
#     file_info = File.get_user_file(user_id, file_id)
#     if not file_info:
#         return jsonify({'error': 'File not found'}), 404
#
#     directory = os.path.dirname(file_info[2])
#     filename = os.path.basename(file_info[2])
#     return send_from_directory(directory, filename, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    token = request.form.get('token')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 生成时间戳文件名（保留原始扩展名）
    original_ext = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().isoformat().replace(":", "_")  # 替换冒号避免文件系统问题
    new_filename = f"{timestamp}{original_ext}"

    # 存储文件
    save_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, new_filename)
    file.save(filepath)

    # 记录到数据库（需要修改File模型）
    File.save_file(user_id, new_filename, filepath)
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': new_filename
    }), 201


@app.route('/download', methods=['GET'])  # 修改路由去掉file_id
def download_file():
    token = request.args.get('token')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # 获取最新文件
    file_info = File.get_latest_user_file(user_id)
    if not file_info:
        return jsonify({'error': 'No files found'}), 404

    directory = os.path.dirname(file_info.filepath)
    filename = os.path.basename(file_info.filepath)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/has_workspace', methods=['GET'])
def has_workspace():
    token = request.args.get('token')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # 检查用户是否有上传的文件
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM files WHERE user_id = %s', (user_id,))
    count = cursor.fetchone()[0]

    return jsonify({'has_workspace': count > 0})



@app.route('/download_json', methods=['GET'])
def download_file_json():
    token = request.args.get('token')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired token'}), 401

    file_info = File.get_latest_user_file(user_id)
    if not file_info:
        return jsonify({'error': 'No files found'}), 404

    try:
        with open(file_info.filepath, 'r') as f:
            file_content = json.load(f)
            return jsonify({
                'filename': file_info.filename,
                'content': file_content
            })
    except json.JSONDecodeError:
        return jsonify({'error': 'File is not valid JSON'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/download/intro', methods=['GET'])
def download_intro():
    token = request.args.get('token')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': '无效或过期的token'}), 401
    return send_from_directory(Config.PUBLIC_FOLDER, 'intro.pdf', as_attachment=True)

@app.route('/download/tech-doc', methods=['GET'])
def download_tech_doc():
    token = request.args.get('token')
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': '无效或过期的token'}), 401
    return send_from_directory(Config.PUBLIC_FOLDER, 'tech_doc.pdf', as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True, port=5000)