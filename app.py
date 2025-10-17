from flask import Flask, request, jsonify, send_from_directory
from models import mysql, User, File, init_db, Register
from utils import generate_token, verify_token, hash_password, check_password
from config import Config
from functools import wraps
import os
from flask_cors import CORS

from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
init_db(app)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') or request.form.get('token')

        # Verifying token validity
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': '无效或过期的token'}), 401

        # query user role
        user = User.get_role_by_id(user_id)
        if not user or user[0] != 'admin':
            return jsonify({'error': '管理员权限不足'}), 403
        return f(*args, **kwargs)

    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') or request.form.get('token')

        # Verifying token validity
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': '无效或过期的token'}), 401

        # query user role
        user = User.get_role_by_id(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        return f(*args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    note = data.get('note', '')

    # Verifying username validity
    if User.get_by_username(username):
        return jsonify({'error': '重复的用户名'}), 400

    # create a registrations
    hashed_pw = hash_password(password)
    if Register.create(username, hashed_pw, note):
        return jsonify({'message': '注册申请已提交'}), 201
    else:
        return jsonify({'error': '注册失败'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    user = User.get_by_username(username)
    if user and check_password(user[2], password) and user[3] == 0:
        token = generate_token(user[0])
        return jsonify({'token': token,'role': user[4]})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/admin/registrations', methods=['GET'])
@admin_required
def registrations():
    approve_status = request.args.get('approve', 0)
    registrations = Register.get_by_approve(approve_status)
    return jsonify({'array': registrations})

@app.route('/admin/approve', methods=['GET'])
@admin_required
def approve():
    reg_id = request.args.get('id')
    reg = Register.get_by_reg_id(reg_id)

    # check name conflict
    if User.get_by_username(reg[1]):
        return jsonify({'error': '用户名已存在'}), 400

    Register.approve_register(reg_id)
    return jsonify({'message': '审批通过'})

@app.route('/admin/getUsers', methods=['GET'])
@admin_required
def getUsers():
    users = User.get_all_user()
    return jsonify({'array': users})

@app.route('/admin/disable_user', methods=['POST'])
@admin_required
def disable_user():
    user_id = request.form.get('user_id')

    try:
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        # 校验管理员权限
        if user[4] == 'admin':
            return jsonify({"code": 403, "message": "管理员账户不可注销"}), 403

        # 校验当前状态
        if user[3] == 1:
            return jsonify({"code": 409, "message": "用户已注销，无需重复操作"}), 409

        User.update_status(user_id, 1)
        return jsonify({"code": 200, "message": "用户注销成功"})

    except Exception as e:
        app.logger.error(f"数据库操作失败: {str(e)}")
        return jsonify({"code": 500, "message": "服务器内部错误"}), 500

@app.route('/admin/update_note', methods=['POST'])
@admin_required
def update_note():
    user_id = request.form.get('user_id')
    new_note = request.form.get('note')
    User.update_note(user_id, new_note)
    return jsonify({'message': '备注已更新'})

@app.route('/uploadWorkspace', methods=['POST'])
@login_required
def uploadWorkspace():
    token = request.form.get('token')
    user_id = verify_token(token)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = request.form.get('filename')
    if filename == '' or filename is None:
        return jsonify({
            'message': 'workspace name can not be none'
        }), 402

    # 生成时间戳文件名（保留原始扩展名）
    original_ext = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().isoformat().replace(":", "_")
    new_filename = f"{timestamp}{original_ext}"

    # 存储文件
    save_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, new_filename)
    file.save(filepath)

    # 记录到数据库（需要修改File模型）
    try:
        File.save_file(user_id, filename, filepath)
    except ValueError as e:
        return jsonify({
            'message': 'workspace name duplicate'
        }), 402
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': new_filename
    }), 201

@app.route('/overwriteWorkspace', methods=['POST'])
@login_required
def overwriteWorkspace():
    token = request.form.get('token')
    user_id = verify_token(token)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = request.form.get('filename')
    if filename == '' or filename is None:
        return jsonify({
            'message': 'workspace name can not be none'
        }), 402

    # 生成时间戳文件名（保留原始扩展名）
    original_ext = os.path.splitext(file.filename)[1]
    timestamp = datetime.now().isoformat().replace(":", "_")
    new_filename = f"{timestamp}{original_ext}"

    # 存储文件
    save_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, new_filename)
    file.save(filepath)

    # 记录到数据库（需要修改File模型）
    try:
        File.overwrite_file(user_id, filename, filepath)
    except ValueError as e:
        return jsonify({
            'message': 'workspace name duplicate'
        }), 402
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': new_filename
    }), 201

@app.route('/get_workspace', methods=['GET'])
@login_required
def get_workspace():
    token = request.args.get('token')
    user_id = verify_token(token)

    # get all workspace of user
    files = File.get_user_files(user_id)
    return jsonify({'files': files})

@app.route('/download_json_workspace', methods=['POST'])
@login_required
def download_json_workspace():
    token = request.form.get('token')
    filename = request.form.get('filename')
    user_id = verify_token(token)

    file_path = File.get_user_file(user_id, filename)
    if not file_path:
        return jsonify({'error': 'No files found'}), 404

    try:
        with open(file_path, 'r') as f:
            file_content = json.load(f)
            return jsonify({
                'filename': filename,
                'content': file_content  # 返回JSON内容
            })
    except json.JSONDecodeError:
        return jsonify({'error': 'File is not valid JSON'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/getString/intro', methods=['GET'])
@login_required
def getString_intro():
    try:
        file_path = os.path.join(Config.PUBLIC_FOLDER, 'intro.md')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return jsonify({'text': content}), 200
    except FileNotFoundError:
        return jsonify({'error': '文档不存在'}), 404
    except Exception as e:
        app.logger.error(f"文档读取失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/getString/tech-doc', methods=['GET'])
@login_required
def getString_tech_doc():
    try:
        file_path = os.path.join(Config.PUBLIC_FOLDER, 'tech_doc.md')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return jsonify({'text': content}), 200
    except FileNotFoundError:
        return jsonify({'error': '文档不存在'}), 404
    except Exception as e:
        app.logger.error(f"文档读取失败: {str(e)}")
        return jsonify({'error': '服务器内部错误'}), 500

# @app.route('/download/intro', methods=['GET'])
# @login_required
# def download_intro():
#     return send_from_directory(Config.PUBLIC_FOLDER, 'intro.pdf', as_attachment=True)
#
# @app.route('/download/tech-doc', methods=['GET'])
# @login_required
# def download_tech_doc():
#     return send_from_directory(Config.PUBLIC_FOLDER, 'tech_doc.pdf', as_attachment=True)

@app.route('/public/images/<filename>')
def serve_image(filename):
    print(filename)
    return send_from_directory(
        os.path.join(app.config['PUBLIC_FOLDER'], 'images'),
        filename
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0' ,debug=True, port=5001)
