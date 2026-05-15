from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default='cliente')
    activo = db.Column(db.Boolean, default=True)

    # relaciones
    motos = db.relationship('Moto', backref='propietario', lazy=True, cascade="all, delete-orphan")
    citas = db.relationship('Cita', backref='cliente', lazy=True, cascade="all, delete-orphan")

    def is_admin(self):
        return self.rol == 'admin'

    def is_empleado(self):
        return self.rol in ['admin', 'empleado']

    def __repr__(self):
        return f'<User {self.username}>'