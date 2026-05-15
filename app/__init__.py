from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_mail import Mail
import os

# 🔌 extensiones
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ⚙️ configuración
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brazo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 📧 config de correo
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@brazo.com')

    # 🔌 inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # 🔐 login config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Debes iniciar sesión para acceder."
    login_manager.login_message_category = "warning"

    # 👤 loader usuario
    from app.models.user import User
    

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 📦 BLUEPRINTS
    from app.routes.auth import auth_bp
    from app.routes.home import home_bp
    from app.routes.moto_route import motos_bp
    from app.routes.cita_route import citas_bp
    from app.routes.admin import admin_bp
    from app.routes.repuesto_route import repuestos_bp
    from app.routes.cliente_routes import clientes_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(home_bp)
    app.register_blueprint(clientes_bp,url_prefix='/cliente')
    app.register_blueprint(motos_bp, url_prefix='/motos')
    app.register_blueprint(citas_bp, url_prefix='/citas')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(repuestos_bp, url_prefix='/repuestos')
    from app.routes.carrito_routes import carrito_bp
    app.register_blueprint(carrito_bp, url_prefix='/carrito')

    # 🛠 crear BD + admin por defecto
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(username='admin').first()

        if not admin:
            admin = User(
                nombre_completo='Administrador',
                username='admin',
                email='admin@brazo.com',
                telefono='0000000000',
                rol='admin',
                password=generate_password_hash('admin123'),
                activo=True
            )
            db.session.add(admin)
            db.session.commit()

    return app