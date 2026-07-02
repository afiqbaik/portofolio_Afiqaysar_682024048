from flask import Blueprint, jsonify, request
from model import Database
from Backend.admin.login import token_required

profil_bp = Blueprint('profil', __name__)


@profil_bp.route('/profil', methods=['GET'])
def get_public_profile():
    try:
        db = Database()
        profile = db.execute_query("SELECT * FROM profiles ORDER BY id DESC LIMIT 1", fetch=True)
        return jsonify({'success': True, 'data': profile[0] if profile else {}}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500


@profil_bp.route('/profil', methods=['POST', 'PUT'])
@token_required
def save_public_profile(current_user):
    try:
        data = request.get_json(silent=True) or {}
        db = Database()
        fields = ['nama_lengkap', 'nama_panggilan', 'email', 'telepon', 'universitas', 'fakultas', 'prodi', 'semester', 'alamat', 'foto_url', 'about_me', 'cv_url', 'social_links']
        values = []
        updates = []

        for field in fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])

        if not updates:
            return jsonify({'success': False, 'error': 'Tidak ada data valid'}), 400

        existing = db.execute_query("SELECT id FROM profiles WHERE user_id = %s", (current_user,), fetch=True)
        if existing:
            values.append(current_user)
            query = f"UPDATE profiles SET {', '.join(updates)} WHERE user_id = %s"
        else:
            values.insert(0, current_user)
            columns = ', '.join([f.split(' = ')[0] for f in updates])
            placeholders = ', '.join(['%s'] * len(updates))
            query = f"INSERT INTO profiles (user_id, {columns}) VALUES (%s, {placeholders})"

        db.execute_query(query, tuple(values))
        return jsonify({'success': True, 'message': 'Profil berhasil disimpan'}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500
