from flask import Blueprint, jsonify
from model import Database

utama_bp = Blueprint('utama', __name__)


@utama_bp.route('/main-profile', methods=['GET'])
def get_main_profile():
    try:
        db = Database()
        profile_query = "SELECT * FROM profiles ORDER BY id DESC LIMIT 1"
        profile_result = db.execute_query(profile_query, fetch=True)
        profile = profile_result[0] if profile_result else {}

        skills_query = "SELECT * FROM skills ORDER BY id DESC"
        skills = db.execute_query(skills_query, fetch=True) or []

        experiences_query = "SELECT * FROM experiences ORDER BY created_at DESC"
        experiences = db.execute_query(experiences_query, fetch=True) or []

        projects_query = "SELECT * FROM projects ORDER BY created_at DESC"
        projects = db.execute_query(projects_query, fetch=True) or []

        return jsonify({
            'success': True,
            'data': {
                **profile,
                'skills': skills,
                'experiences': experiences,
                'projects': projects,
            }
        }), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500


@utama_bp.route('/contact', methods=['POST'])
def contact():
    from flask import request
    from config import Config

    try:
        data = request.get_json(silent=True) or {}
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        message = (data.get('message') or '').strip()

        if not all([name, email, message]):
            return jsonify({'success': False, 'error': 'Semua field wajib diisi'}), 400

        if '@' not in email:
            return jsonify({'success': False, 'error': 'Format email tidak valid'}), 400

        try:
            import resend
            client = resend.Emails()
            client.send(
                {
                    'from': Config.RESEND_FROM,
                    'to': [Config.CONTACT_EMAIL],
                    'reply_to': email,
                    'subject': f'Portfolio contact from {name}',
                    'html': f'<p><strong>Name:</strong> {name}</p><p><strong>Email:</strong> {email}</p><p><strong>Message:</strong><br/>{message}</p>',
                }
            )
        except Exception as exc:
            return jsonify({'success': False, 'error': f'Gagal mengirim pesan: {exc}'}), 502

        return jsonify({'success': True, 'message': 'Pesan berhasil dikirim'}), 200
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 500
