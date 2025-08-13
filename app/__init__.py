import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32))
    app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'frames'))
    app.config['PHOTOS_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'photos'))
    app.config['SETTINGS_PATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json'))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PHOTOS_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['SETTINGS_PATH']), exist_ok=True)

    # Blueprints
    from .routes.photobooth import bp as photobooth_bp
    from .routes.settings import bp as settings_bp
    from .routes.gallery import bp as gallery_bp
    from .routes.tts import bp as tts_bp

    app.register_blueprint(photobooth_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(tts_bp)

    # Respect X-Forwarded-* when behind nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    return app


# Flask CLI entry
app = create_app()
