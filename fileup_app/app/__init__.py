import os

import logging

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = config_class.SECRET_KEY

    #  A more verbose logging level can be enabled (WARNING is the default).
    if "LogDebug" in app.config.get("ENABLE_FEATURES", ""):
        app.logger.setLevel(logging.DEBUG)
    elif "LogInfo" in app.config.get("ENABLE_FEATURES", ""):
        app.logger.setLevel(logging.INFO)

    app.logger.info(f"create_app: version={app.config.get('FILEUP_VERSION')}")

    #  Configure for running behind a proxy.
    proxy_level = app.config.get("PROXY_LEVEL", 0)
    app.logger.info(f"PROXY_LEVEL={proxy_level}")
    if 0 < proxy_level:
        #  From looking at logged request headers, it appears that the proxy
        #  in front of an Azure Python WebApp uses only the 'X-Forwarded-For'
        #  and 'X-Forwarded-Proto' headers.
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=proxy_level,
            x_proto=proxy_level,
        )

    #  Register Flask blueprints.
    from app.auth.routes import bp as auth_bp
    from app.main import bp as main_bp
    from app.storage.routes import bp as storage_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(storage_bp)

    #  Create upload destination if needed.
    upload_path = app.config.get("UPLOAD_PATH")
    if upload_path:
        upload_path = os.path.abspath(upload_path)
        if not os.path.exists(upload_path):
            app.logger.info(f"create_app: mkdir {upload_path}")
            os.mkdir(upload_path)

    return app
