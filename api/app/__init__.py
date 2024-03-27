from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config
from .extentions import scheduler
import logging
import os

db = SQLAlchemy()
app = Flask(__name__)


def create_app():

    def is_debug_mode():
        """Get app debug status."""
        debug = os.environ.get("FLASK_DEBUG")
        if not debug:
            return os.environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():
        """Get werkzeug status."""
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    
    app = Flask(__name__)
    app.config.from_object(Config)
    scheduler.init_app(app)
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    CORS(app)

    # 다른 설정 및 확장 추가 가능 
    db.init_app(app)

    # Flask 애플리케이션 컨텍스트 설정
    with app.app_context():
        from .routes import nok_info_routes, dementia_info_routes, is_connected_routes, location_info_routes, send_location_info_routes, user_login_routes, user_info_modification_routes, caculate_dementia_avarage_walking_speed_routes, get_user_info_routes, update_rate_routes, send_meaningful_location_info_routes
        app.register_blueprint(nok_info_routes)
        app.register_blueprint(dementia_info_routes)
        app.register_blueprint(is_connected_routes)
        app.register_blueprint(location_info_routes)
        app.register_blueprint(send_location_info_routes)
        app.register_blueprint(user_login_routes)
        app.register_blueprint(user_info_modification_routes)
        app.register_blueprint(caculate_dementia_avarage_walking_speed_routes)
        app.register_blueprint(get_user_info_routes)
        app.register_blueprint(update_rate_routes)
        app.register_blueprint(send_meaningful_location_info_routes)
        

    scheduler.start()
        

    

    return app