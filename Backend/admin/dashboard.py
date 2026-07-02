from flask import Blueprint, jsonify
from model import Database
from Backend.admin.login import token_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Mengambil statistik dashboard untuk admin"""
    try:
        db = Database()
        stats = {}
        
        query = "SELECT COUNT(*) as count FROM experiences WHERE user_id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)
        stats['experiences_count'] = result[0]['count'] if result else 0
        
        query = "SELECT COUNT(*) as count FROM projects WHERE user_id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)
        stats['projects_count'] = result[0]['count'] if result else 0
        
        query = "SELECT COUNT(*) as count FROM skills WHERE user_id = %s"
        result = db.execute_query(query, (current_user,), fetch=True)
        stats['skills_count'] = result[0]['count'] if result else 0
        
        query = "SELECT username FROM users WHERE id = %s LIMIT 1"
        result = db.execute_query(query, (current_user,), fetch=True)
        stats['admin_name'] = result[0]['username'] if result else 'Admin'
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/dashboard/recent', methods=['GET'])
@token_required
def get_recent_activity(current_user):
    """Mengambil aktivitas terbaru"""
    try:
        db = Database()
        activities = []
        
        query_exp = """
            SELECT id, posisi, perusahaan, durasi, created_at, 'experience' as type 
            FROM experiences 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 3
        """
        result_exp = db.execute_query(query_exp, (current_user,), fetch=True)
        if result_exp:
            activities.extend(result_exp)
        
        query_proj = """
            SELECT id, judul, deskripsi, created_at, 'project' as type 
            FROM projects 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 3
        """
        result_proj = db.execute_query(query_proj, (current_user,), fetch=True)
        if result_proj:
            activities.extend(result_proj)
        
        activities.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': activities[:5] 
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500