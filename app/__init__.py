from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # 다른 설정 및 확장 추가 가능

    db.init_app(app)

    from .routes import nok_info_routes, dementia_info_routes, location_info_routes
    app.register_blueprint(nok_info_routes)
    app.register_blueprint(dementia_info_routes)
    app.register_blueprint(location_info_routes)

    return app

def create_db():
    with db.app.app_context():
        if not os.path.exists('website/' + db.engine.url.database):
            db.create_all()