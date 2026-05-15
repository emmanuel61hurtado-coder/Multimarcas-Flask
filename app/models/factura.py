from app import db
from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'facturas'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False) # Ej: FAC-001
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones - Llaves foráneas
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    moto_id = db.Column(db.Integer, db.ForeignKey('motos.id'), nullable=True)
    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'), nullable=True)
    
    # Relaciones - Objetos
    user = db.relationship('User', foreign_keys=[user_id], backref='facturas', lazy=True)
    empleado = db.relationship('User', foreign_keys=[empleado_id], backref='facturas_asignadas', lazy=True)
    moto = db.relationship('Moto', backref='facturas', lazy=True)
    cita = db.relationship('Cita', backref='factura_rel', lazy=True)
    
    # Visibilidad
    visible_cliente = db.Column(db.Boolean, default=True)
    
    # Totales
    subtotal = db.Column(db.Float, default=0.0)
    iva = db.Column(db.Float, default=0.0) # 19% o lo que prefieras
    total = db.Column(db.Float, default=0.0)
    metodo_pago = db.Column(db.String(50)) # Efectivo, Transferencia, etc.

    # Calificación del servicio
    calificacion = db.Column(db.Integer, nullable=True) # 1 a 5
    comentario_cliente = db.Column(db.String(500), nullable=True)
    
    items = db.relationship('DetalleFactura', backref='factura', lazy=True, cascade="all, delete-orphan")

class DetalleFactura(db.Model):
    __tablename__ = 'detalle_facturas'

    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    
    descripcion = db.Column(db.String(200), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
