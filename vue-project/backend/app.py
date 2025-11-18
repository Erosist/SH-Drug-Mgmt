from flask import Flask
from config import DevelopmentConfig
from extensions import db, migrate, jwt
from auth import bp as auth_bp
from catalog import bp as catalog_bp
from enterprise import bp as enterprise_bp
from admin import bp as admin_bp


def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(enterprise_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return {'msg': 'Flask auth backend is running'}

    return app
