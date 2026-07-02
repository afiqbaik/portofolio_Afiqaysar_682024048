from flask import Blueprint, jsonify, request
from model import Database
from Backend.admin.login import token_required

akun_bp = Blueprint('akun', __name__)


@akun_bp.route('/akun', methods=['GET'])
@token_required
def get_akun(current_user):
    try:
        db = Database()
        result = db.execute_query("SELECT id, username, role FROM users WHERE id = %s", (current_user,), fetch=True)
        return jsonify({'success': True, 'data': result[0] if result else {}}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500


@akun_bp.route('/akun', methods=['PUT'])
@token_required
def update_akun(current_user):
    try:
        data = request.get_json(silent=True) or {}
        db = Database()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not username:
            return jsonify({'success': False, 'error': 'Username wajib diisi'}), 400

        updates = ['username = %s']
        values = [username]
        if password:
            from werkzeug.security import generate_password_hash
            updates.append('password_hash = %s')
            values.append(generate_password_hash(password))

        values.append(current_user)
        db.execute_query(f"UPDATE users SET {', '.join(updates)} WHERE id = %s", tuple(values))
        return jsonify({'success': True, 'message': 'Akun berhasil diupdate'}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500
