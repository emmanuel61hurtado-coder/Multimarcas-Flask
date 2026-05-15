from app import db

class Moto(db.Model):
    __tablename__ = 'motos'

    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(80), nullable=False)
    modelo = db.Column(db.String(80), nullable=False)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    año = db.Column(db.Integer)
    color = db.Column(db.String(40))
    cilindraje = db.Column(db.String(20))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relación inversa (ya viene por User.motos)
    citas = db.relationship('Cita', backref='moto', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Moto {self.marca} {self.modelo} - {self.placa}>'