from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.cita import Cita
from app.models.moto import Moto
from app.models.factura import Factura
from app.models.pedido import Pedido

clientes_bp = Blueprint('cliente', __name__)


# 🏠 DASHBOARD + CITAS
@clientes_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 🏍️ MOTOS DEL CLIENTE
    motos = Moto.query.filter_by(user_id=current_user.id).all()
    # 🧾 ÚLTIMAS FACTURAS (Solo las visibles)
    facturas = Factura.query.filter_by(user_id=current_user.id, visible_cliente=True).order_by(Factura.fecha.desc()).limit(5).all()

    return render_template(
        'cliente/dashboard.html',
        motos=motos,
        facturas=facturas
    )

@clientes_bp.route('/mis-pedidos')
@login_required
def mis_pedidos():
    pedidos = Pedido.query.filter_by(user_id=current_user.id).order_by(Pedido.fecha.desc()).all()
    return render_template('cliente/mis_pedidos.html', pedidos=pedidos)


# 🏍️ MOTOS
@clientes_bp.route('/motos')
@login_required
def motos():
    motos = Moto.query.filter_by(user_id=current_user.id).all()
    return render_template(
        'cliente/motos.html',
        motos=motos
    )


@clientes_bp.route('/motos/nueva', methods=['POST'])
@login_required
def agregar_moto():
    marca = request.form.get('marca')
    modelo = request.form.get('modelo')
    placa = request.form.get('placa', '').upper()
    año = request.form.get('año')
    color = request.form.get('color')
    cilindraje = request.form.get('cilindraje')

    if not all([marca, modelo, placa]):
        flash('Marca, Modelo y Placa son obligatorios.', 'danger')
        return redirect(url_for('cliente.motos'))

    # Verificar si la placa ya existe
    moto_existente = Moto.query.filter_by(placa=placa).first()
    if moto_existente:
        flash('Esta placa ya está registrada en el sistema.', 'warning')
        return redirect(url_for('cliente.motos'))

    nueva_moto = Moto(
        marca=marca,
        modelo=modelo,
        placa=placa,
        año=año,
        color=color,
        cilindraje=cilindraje,
        user_id=current_user.id
    )

    try:
        db.session.add(nueva_moto)
        db.session.commit()
        flash('Moto registrada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al registrar la moto.', 'danger')

    return redirect(url_for('cliente.motos'))


# 🧾 HISTORIAL Y FACTURAS
@clientes_bp.route('/historial')
@login_required
def historial():
    # Obtener todas las citas del cliente que estén marcadas como "completada"
    trabajos = Cita.query.filter_by(user_id=current_user.id, estado='completada').order_by(Cita.fecha.desc()).all()
    
    # Obtener todas las facturas reales del cliente (Solo las visibles)
    facturas = Factura.query.filter_by(user_id=current_user.id, visible_cliente=True).order_by(Factura.fecha.desc()).all()

    return render_template(
        'cliente/historial.html',
        trabajos=trabajos,
        facturas=facturas
    )

@clientes_bp.route('/factura/<int:fid>/eliminar', methods=['POST'])
@login_required
def eliminar_factura(fid):
    # Obtener factura y verificar que pertenezca al usuario actual
    factura = Factura.query.get_or_404(fid)
    
    if factura.user_id != current_user.id:
        flash('No tienes permiso para eliminar esta factura.', 'danger')
        return redirect(url_for('cliente.historial'))
        
    numero = factura.numero
    
    # En lugar de eliminar de la base de datos (db.session.delete(factura)),
    # solo la ocultamos del panel del cliente para no afectar la contabilidad del administrador.
    factura.visible_cliente = False
    db.session.commit()
    
    flash(f'Comprobante {numero} ocultado de tu historial.', 'success')
    return redirect(url_for('cliente.historial'))

@clientes_bp.route('/factura/<int:fid>/calificar', methods=['POST'])
@login_required
def calificar_servicio(fid):
    factura = Factura.query.get_or_404(fid)
    
    if factura.user_id != current_user.id:
        flash('No tienes permiso para calificar este servicio.', 'danger')
        return redirect(url_for('cliente.historial'))
    
    try:
        rating = int(request.form.get('calificacion'))
        comentario = request.form.get('comentario', '').strip()
        
        if 1 <= rating <= 5:
            factura.calificacion = rating
            factura.comentario_cliente = comentario
            db.session.commit()
            flash('¡Gracias por calificar nuestro servicio! Tu opinión nos ayuda a mejorar.', 'success')
        else:
            flash('Calificación inválida.', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash('Ocurrió un error al procesar tu calificación.', 'danger')
        
    return redirect(url_for('cliente.historial'))