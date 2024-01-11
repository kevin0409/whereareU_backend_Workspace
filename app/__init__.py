from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 다른 설정 및 확장 추가 가능

    db.init_app(app)

    from .routes import nok_info_routes, dementia_info_routes, location_info_routes
    app.register_blueprint(nok_info_routes)
    app.register_blueprint(dementia_info_routes)
    app.register_blueprint(location_info_routes)

    return app