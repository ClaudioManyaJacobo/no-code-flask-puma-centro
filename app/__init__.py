from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar Blueprints
    from app.routes.usuario_routes import usuario_bp
    from app.routes.factura_routes import factura_bp
    from app.routes.sector_routes import sector_bp

    app.register_blueprint(usuario_bp, url_prefix='/usuarios')
    app.register_blueprint(factura_bp, url_prefix='/facturas')
    app.register_blueprint(sector_bp, url_prefix='/sectores')

    return app
