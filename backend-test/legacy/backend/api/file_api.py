from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename

file_bp = Blueprint('file', __name__)

UPLOAD_FOLDER = '/home/parry-wsl/study/database/interface-test/backend-test/backend/files'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@file_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 这里可以添加文献解析逻辑
        # 然后将解析结果存入数据库
        
        return jsonify({
            'filename': filename,
            'path': filepath,
            'message': 'File uploaded successfully'
        }), 200
    
    return jsonify({'error': 'File type not allowed'}), 400