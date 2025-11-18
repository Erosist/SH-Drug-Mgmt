from flask import Flask
from config import DevelopmentConfig
from extensions import db, migrate, jwt
from auth import bp as auth_bp


def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return {'msg': 'Flask auth backend is running'}

    return app
