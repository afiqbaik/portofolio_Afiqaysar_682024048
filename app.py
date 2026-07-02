import os
import tempfile
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from config import Config

from Backend.admin.login import login_bp
from Backend.admin.dashboard import dashboard_bp
from Backend.admin.profiles import profiles_bp
from Backend.admin.akun import akun_bp
from Backend.admin.experience import experience_bp
from Backend.admin.projects import projects_bp
from Backend.admin.skills import skills_bp
from Backend.admin.upload import upload_bp
from Backend.utama.utama import utama_bp
from Backend.profil.profil import profil_bp


def create_app():
    app = Flask(__name__, static_folder='Frontend', template_folder='.')
    app.config.from_object(Config)
    # attempt to create configured upload folder; fallback to system temp if not possible
    try:
        app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        temp_dir = os.path.join(tempfile.gettempdir(), 'uploads')
        try:
            os.makedirs(temp_dir, exist_ok=True)
            app.config['UPLOAD_FOLDER'] = temp_dir
            app.logger.warning(f"Configured UPLOAD_FOLDER unavailable; using temp folder: {temp_dir} ({e})")
        except Exception:
            # as a last resort use current working directory path (read-only environments still may fail)
            fallback = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(fallback, exist_ok=True)
            app.config['UPLOAD_FOLDER'] = fallback
            app.logger.warning(f"Upload folder fallback used: {fallback}")

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(profiles_bp, url_prefix='/api')
    app.register_blueprint(akun_bp, url_prefix='/api')
    app.register_blueprint(experience_bp, url_prefix='/api')
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(skills_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(utama_bp, url_prefix='/api')
    app.register_blueprint(profil_bp, url_prefix='/api')

    @app.route('/')
    def index():
        if os.path.exists(os.path.join(app.root_path, 'index.html')):
            return send_from_directory(app.root_path, 'index.html')
        return "Error: index.html not found", 404

    @app.route('/index.html')
    def index_file():
        return index()

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        return send_from_directory(os.path.join(app.root_path, 'Frontend', 'admin'), filename)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.root_path, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.errorhandler(404)
    def not_found(error):
        if request.accept_mimetypes.best == 'text/html':
            return send_from_directory(app.root_path, 'index.html')
        return jsonify({'success': False, 'error': 'Route tidak ditemukan'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'error': 'Terjadi kesalahan pada server'}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        # Report presence of critical configuration without exposing secrets
        cfg = {
            'db_configured': bool(Config.DB_USER and Config.DB_PASSWORD),
            'cloudinary_configured': bool(Config.CLOUDINARY_CLOUD_NAME and Config.CLOUDINARY_API_KEY and Config.CLOUDINARY_API_SECRET),
            'jwt_configured': bool(Config.JWT_SECRET_KEY),
            'upload_folder': app.config.get('UPLOAD_FOLDER')
        }
        return jsonify({'ok': True, 'config': cfg}), 200

    return app


# Create Flask app instance at top-level for Vercel/WSGI servers
app = create_app()


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, use_reloader=False, host='0.0.0.0', port=5000)