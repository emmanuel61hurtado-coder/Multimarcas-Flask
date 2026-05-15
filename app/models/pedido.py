from datetime import datetime
from app import db

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='Pendiente')
    metodo_entrega = db.Column(db.String(20), nullable=False)
    origen = db.Column(db.String(10), default='Web')  # 'Web' o 'Físico'
    nombre_cliente_fisico = db.Column(db.String(100))  # Para ventas en taller sin cuenta # Taller, Envío
    direccion_envio = db.Column(db.String(200))
    telefono_contacto = db.Column(db.String(20))
    total = db.Column(db.Float, nullable=False)
    
    # Relaciones
    user = db.relationship('User', backref='pedidos')
    items = db.relationship('DetallePedido', backref='pedido', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pedido {self.id} - {self.estado}>'

class DetallePedido(db.Model):
    __tablename__ = 'detalles_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    repuesto_id = db.Column(db.Integer, db.ForeignKey('repuestos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    # Relaciones
    repuesto = db.relationship('Repuesto')

    def __repr__(self):
        return f'<DetallePedido {self.id} - {self.cantidad} unidades>'
