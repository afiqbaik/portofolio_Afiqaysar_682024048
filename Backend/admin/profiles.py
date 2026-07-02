from flask import Blueprint, request, jsonify
from model import Database
from Backend.admin.login import token_required
import re

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/profiles', methods=['GET'])
@token_required
def get_profil(current_user):
    try:
        db = Database()
        query = "SELECT * FROM profiles WHERE user_id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)
        
        if result:
            return jsonify({'success': True, 'data': result[0]}), 200
        else:
            return jsonify({'success': True, 'data': {}}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profiles_bp.route('/profiles', methods=['POST', 'PUT'])
@token_required
def update_profil(current_user):
    try:
        data = request.get_json()
        db = Database()

        check_query = "SELECT id FROM profiles WHERE user_id = %s"
        existing = db.execute_query(check_query, (current_user,), fetch=True)

        allowed_fields = [
            'nama_lengkap', 'nama_panggilan', 'tempat_lahir', 'tanggal_lahir',
            'email', 'telepon', 'universitas', 'fakultas', 'prodi',
            'semester', 'alamat', 'foto_url'
        ]

        updates = []
        values = []

        import datetime
        date_re = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        for field in allowed_fields:
            if field in data:
                val = data[field]
                if val == '':
                    val = None

                if field == 'tanggal_lahir':
                    if val is None:
                        pass
                    elif isinstance(val, str):
                        if ' ' in val:
                            val = val.split(' ')[0]
                        if not date_re.match(val):
                            try:
                                parsed = datetime.datetime.fromisoformat(val)
                                val = parsed.date().isoformat()
                            except Exception:
                                val = None
                    else:
                        try:
                            val = datetime.date(val).isoformat()
                        except Exception:
                            val = None

                updates.append(f"{field} = %s")
                values.append(val)

        if not updates:
            return jsonify({'error': 'Tidak ada data valid untuk diupdate'}), 400

        if existing:
            values.append(current_user)
            query = f"UPDATE profiles SET {', '.join(updates)} WHERE user_id = %s"
        else:
            fields_str = ', '.join([f.split(' = ')[0] for f in updates])
            placeholders = ', '.join(['%s'] * len(updates))
            values.insert(0, current_user) 
            query = f"INSERT INTO profiles (user_id, {fields_str}) VALUES (%s, {placeholders})"

        db.execute_query(query, tuple(values))
        
        return jsonify({'success': True, 'message': 'Profil berhasil disimpan'}), 200

    except Exception as e:
        print(f"DEBUG ERROR PROFIL: {str(e)}") 
        return jsonify({'error': str(e)}), 500