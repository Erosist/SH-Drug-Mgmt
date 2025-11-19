from flask import Flask
from flask_cors import CORS
from config import DevelopmentConfig
from extensions import db, migrate, jwt
from auth import bp as auth_bp
from supply import bp as supply_bp
from catalog import bp as catalog_bp
from orders import bp as orders_bp
from inventory_warning import bp as inventory_bp

def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # init CORS
    CORS(app, 
         origins=['http://localhost:5174', 'http://localhost:5173', 'http://127.0.0.1:5174', 'http://127.0.0.1:5173'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(supply_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(inventory_bp)

    @app.route('/')
    def index():
        return {'msg': 'Flask auth backend is running'}

    return app
