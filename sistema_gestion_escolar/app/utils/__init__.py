# app/__init__.py

from flask import Flask
from flask_login import LoginManager # Asegúrate de importar LoginManager
from app.config import Config
from app.models.db import DB
from app.models.usuario import Usuario # Necesario para el user_loader

# Inicializar Flask-Login
login_manager = LoginManager() # <--- Asegúrate de que esta línea esté aquí, a nivel global o antes de create_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar la base de datos
    DB.init(app.config)

    # Inicializar Flask-Login con la aplicación
    login_manager.init_app(app) # <--- ¡ESTA ES LA LÍNEA CLAVE!
    login_manager.login_view = 'auth_bp.login' # Define la ruta de login

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Asegúrate de que tu modelo Usuario tenga un método para buscar por ID/username
        return Usuario.find_by_username(user_id)

    # Importar y registrar Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp
    from app.routes.docente import docente_bp
    from app.routes.estudiante import estudiante_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(docente_bp)
    app.register_blueprint(estudiante_bp)

    return app