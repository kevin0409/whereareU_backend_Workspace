from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:000409@127.0.0.1:3306/testdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 다른 설정 및 확장 추가 가능

    db.init_app(app)

    from .routes import nok_info_routes, dementia_info_routes
    app.register_blueprint(nok_info_routes)
    app.register_blueprint(dementia_info_routes)

    return app
