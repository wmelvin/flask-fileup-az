import os
from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = config_class.SECRET_KEY

    from app.auth.routes import bp as auth_bp
    from app.main import bp as main_bp
    from app.storage.routes import bp as storage_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(storage_bp)

    upload_path = app.config["UPLOAD_PATH"]
    if upload_path:
        upload_path = os.path.abspath(upload_path)
        if not os.path.exists(upload_path):
            print(f"create_app: mkdir {upload_path}")
            os.mkdir(upload_path)

    return app
