import os
import tempfile
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from config import Config

# Import blueprints inside create_app() to avoid import-time crashes in serverless


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

    # register blueprints with guarded imports so an import error doesn't crash app
    def try_register(module_path, bp_name='bp'):
        try:
            module = __import__(module_path, fromlist=['*'])
            bp = getattr(module, bp_name, None)
            if bp is None:
                app.logger.warning(f"Module {module_path} imported but blueprint '{bp_name}' not found")
                return False
            app.register_blueprint(bp, url_prefix='/api')
            return True
        except Exception as exc:
            app.logger.exception(f"Failed to import/register {module_path}: {exc}")
            # create a placeholder route to indicate the feature is unavailable
            route_base = '/api'
            @app.route(f"{route_base}/{module_path.replace('.', '/')}")
            def _bp_unavailable():
                return jsonify({'error': f'Module {module_path} unavailable'}), 503
            return False

    try_register('Backend.admin.login', 'login_bp')
    try_register('Backend.admin.dashboard', 'dashboard_bp')
    try_register('Backend.admin.profiles', 'profiles_bp')
    try_register('Backend.admin.akun', 'akun_bp')
    try_register('Backend.admin.experience', 'experience_bp')
    try_register('Backend.admin.projects', 'projects_bp')
    try_register('Backend.admin.skills', 'skills_bp')
    try_register('Backend.admin.upload', 'upload_bp')
    try_register('Backend.utama.utama', 'utama_bp')
    try_register('Backend.profil.profil', 'profil_bp')

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