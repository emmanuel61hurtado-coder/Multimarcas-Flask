from app import db

class Trabajo(db.Model):
    __tablename__ = 'trabajos'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)

    mecanico = db.Column(db.String(100))
    repuestos = db.Column(db.Text)
    costo = db.Column(db.Float)

    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'))