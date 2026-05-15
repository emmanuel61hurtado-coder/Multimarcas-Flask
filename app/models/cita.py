from app import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = 'citas'

    id = db.Column(db.Integer, primary_key=True)

    # 🔥 IMPORTANTE: coincide con users y motos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    moto_id = db.Column(db.Integer, db.ForeignKey('motos.id'), nullable=False)

    fecha = db.Column(db.DateTime, nullable=False)

    tipo_servicio = db.Column(db.String(80), nullable=False)
    descripcion = db.Column(db.String(200))

    estado = db.Column(db.String(20), default="pendiente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Cita {self.fecha} - {self.estado}>'