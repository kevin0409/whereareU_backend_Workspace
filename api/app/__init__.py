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

    from .routes import nok_info_routes, dementia_info_routes, is_connected_routes, location_info_routes, send_location_info_routes, user_login_routes, user_info_modification_routes, caculate_dementia_avarage_walking_speed_routes, get_user_info_routes, analyze_schedule

    app.register_blueprint(nok_info_routes)
    app.register_blueprint(dementia_info_routes)
    app.register_blueprint(is_connected_routes)
    app.register_blueprint(location_info_routes)
    app.register_blueprint(send_location_info_routes)
    app.register_blueprint(user_login_routes)
    app.register_blueprint(user_info_modification_routes)
    app.register_blueprint(caculate_dementia_avarage_walking_speed_routes)
    app.register_blueprint(get_user_info_routes)

    app.register_blueprint(analyze_schedule)

    

    return app

def create_db():
    with db.app.app_context():
        if not os.path.exists('website/' + db.engine.url.database):
            db.create_all()