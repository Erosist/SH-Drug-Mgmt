import os
from flask import Flask
from flask_cors import CORS
from config import DevelopmentConfig, ProductionConfig
from extensions import db, migrate, jwt
from auth import bp as auth_bp
from supply import bp as supply_bp
from catalog import bp as catalog_bp
from enterprise import bp as enterprise_bp
from admin import bp as admin_bp
from orders import bp as orders_bp, register_logistics_blueprint
from inventory_warning import bp as inventory_warning_bp
from circulation import bp as circulation_bp
from nearby import bp as nearby_bp

def create_app():
    app = Flask(__name__)

    # 根据环境变量选择配置
    env = os.getenv("FLASK_ENV", "development")
    
    if env == "production":
        app.config.from_object(ProductionConfig)
        print(">>> Using ProductionConfig")
    else:
        app.config.from_object(DevelopmentConfig)
        print(">>> Using DevelopmentConfig")

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
    app.register_blueprint(enterprise_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(inventory_warning_bp)
    app.register_blueprint(circulation_bp)
    app.register_blueprint(nearby_bp)
    
    # register logistics blueprint
    register_logistics_blueprint(app)

    @app.route('/')
    def index():
        return {'msg': 'Flask auth backend is running'}

    return app

app = create_app()

if __name__ == '__main__':
    app.run()
