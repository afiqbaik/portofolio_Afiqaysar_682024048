from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from model import Database
import jwt
import datetime
import logging
from functools import wraps
from config import Config

logger = logging.getLogger(__name__)

login_bp = Blueprint('login', __name__) 

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            token = session.get('token')
        
        if not token:
            return jsonify({'error': 'Token tidak ditemukan'}), 401
        
        try:
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token telah kadaluarsa'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token tidak valid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@login_bp.route('/login', methods=['POST'])
def login():
    """Endpoint untuk login admin"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body harus JSON'}), 400
            
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username dan password wajib diisi'}), 400
        
        db = Database()
        query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
        user = db.execute_query(query, (username,), fetch=True)
        
        if not user:
            return jsonify({'error': 'Username atau password salah'}), 401
        
        user = user[0]
        hash_preview = user['password_hash'][:30] + "..." if len(user['password_hash']) > 30 else user['password_hash']
        logger.info(f"[LOGIN DEBUG] User: {username} | Hash Prefix: {hash_preview}")

        is_valid = False
        try:
            is_valid = check_password_hash(user['password_hash'], password)
        except Exception:
            is_valid = (user['password_hash'] == password)

        if not is_valid:
            logger.warning(f"[LOGIN DEBUG] Password mismatch for user: {username}")
            return jsonify({'error': 'Username atau password salah'}), 401
        
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm='HS256')
        
        session.permanent = True
        session['token'] = token
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        return jsonify({
            'message': 'Login berhasil',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[LOGIN ERROR] {str(e)}")
        return jsonify({'error': 'Terjadi kesalahan pada server'}), 500
@login_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint untuk logout"""
    session.clear()
    
    response = jsonify({'message': 'Logout berhasil'})
    response.delete_cookie('session') 
    return response, 200

@login_bp.route('/auth/check', methods=['GET'])
@token_required
def check_auth(current_user):
    """Cek status autentikasi"""
    return jsonify({
        'authenticated': True,
        'user': {
            'id': current_user,
            'username': session.get('username'),
            'role': session.get('role')
        }
    }), 200