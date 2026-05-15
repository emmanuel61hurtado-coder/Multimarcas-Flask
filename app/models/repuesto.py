from app import db

class Repuesto(db.Model):
    __tablename__ = 'repuestos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(60))
    marca = db.Column(db.String(60))
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    descripcion = db.Column(db.Text)

    def __repr__(self):
        return f'<Repuesto {self.nombre}>'