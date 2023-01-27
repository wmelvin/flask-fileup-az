import os

import logging

# from opencensus.ext.azure.log_exporter import AzureLogHandler

from flask import Flask
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = config_class.SECRET_KEY

    if "LogDebug" in app.config.get("ENABLE_FEATURES", ""):
        app.logger.setLevel(logging.DEBUG)
    elif "LogInfo" in app.config.get("ENABLE_FEATURES", ""):
        app.logger.setLevel(logging.INFO)
    #  The default logging level is WARNING.

    app.logger.info(f"create_app: version={app.config.get('FILEUP_VERSION')}")

    from app.auth.routes import bp as auth_bp
    from app.main import bp as main_bp
    from app.storage.routes import bp as storage_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(storage_bp)

    upload_path = app.config.get("UPLOAD_PATH")
    if upload_path:
        upload_path = os.path.abspath(upload_path)
        if not os.path.exists(upload_path):
            print(f"create_app: mkdir {upload_path}")
            os.mkdir(upload_path)

    return app
