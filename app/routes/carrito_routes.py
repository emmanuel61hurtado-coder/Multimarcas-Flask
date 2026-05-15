from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app import db
from app.models.repuesto import Repuesto
from app.models.pedido import Pedido, DetallePedido

carrito_bp = Blueprint('carrito', __name__)

@carrito_bp.route('/')
@login_required
def ver_carrito():
    if current_user.is_admin() or current_user.is_empleado():
        flash('El carrito es exclusivo para clientes.', 'warning')
        return redirect(url_for('admin.dashboard'))
    
    carrito = session.get('carrito', {})
    items = []
    total = 0
    
    for rid, cantidad in carrito.items():
        rep = Repuesto.query.get(int(rid))
        if rep:
            subtotal = rep.precio * cantidad
            items.append({
                'repuesto': rep,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
            total += subtotal
            
    return render_template('cliente/carrito.html', items=items, total=total)

@carrito_bp.route('/agregar/<int:rid>')
@login_required
def agregar(rid):
    rep = Repuesto.query.get_or_404(rid)
    carrito = session.get('carrito', {})
    
    rid_str = str(rid)
    if rid_str in carrito:
        carrito[rid_str] += 1
    else:
        carrito[rid_str] = 1
        
    session['carrito'] = carrito
    flash(f'{rep.nombre} añadido al carrito.', 'success')
    return redirect(request.referrer or url_for('repuestos.index'))

@carrito_bp.route('/eliminar/<int:rid>')
@login_required
def eliminar(rid):
    carrito = session.get('carrito', {})
    rid_str = str(rid)
    
    if rid_str in carrito:
        del carrito[rid_str]
        session['carrito'] = carrito
        flash('Repuesto eliminado del carrito.', 'info')
        
    return redirect(url_for('carrito.ver_carrito'))

@carrito_bp.route('/cantidad/<int:rid>/<accion>')
@login_required
def cambiar_cantidad(rid, accion):
    carrito = session.get('carrito', {})
    rid_str = str(rid)
    
    if rid_str in carrito:
        if accion == 'mas':
            carrito[rid_str] += 1
        elif accion == 'menos':
            carrito[rid_str] -= 1
            if carrito[rid_str] <= 0:
                del carrito[rid_str]
        session['carrito'] = carrito
        
    return redirect(url_for('carrito.ver_carrito'))

@carrito_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    carrito = session.get('carrito', {})
    if not carrito:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('repuestos.index'))
        
    if request.method == 'POST':
        metodo = request.form.get('metodo_entrega')
        direccion = request.form.get('direccion', '')
        telefono = request.form.get('telefono', '')
        
        if metodo == 'Envío' and not direccion:
            flash('Por favor ingresa una dirección para el envío.', 'danger')
            return redirect(url_for('carrito.ver_carrito'))

        if not telefono:
            flash('Por favor ingresa un teléfono de contacto.', 'danger')
            return redirect(url_for('carrito.ver_carrito'))

        # Calcular total
        total = 0
        items_pedido = []
        for rid, cantidad in carrito.items():
            rep = Repuesto.query.get(int(rid))
            if rep:
                subtotal = rep.precio * cantidad
                total += subtotal
                items_pedido.append((rep, cantidad, subtotal))

        if not items_pedido:
            flash('No hay artículos válidos en el carrito.', 'danger')
            return redirect(url_for('repuestos.index'))

        nuevo_pedido = Pedido(
            user_id=current_user.id,
            metodo_entrega=metodo,
            direccion_envio=direccion if metodo == 'Envío' else None,
            telefono_contacto=telefono,
            total=total
        )
        
        db.session.add(nuevo_pedido)
        
        for rep, cant, st in items_pedido:
            detalle = DetallePedido(
                pedido=nuevo_pedido,
                repuesto_id=rep.id,
                cantidad=cant,
                precio_unitario=rep.precio,
                subtotal=st
            )
            db.session.add(detalle)
            
        db.session.commit()
        
        # Limpiar carrito
        session.pop('carrito', None)
        
        flash('¡Pedido realizado con éxito! Nos pondremos en contacto para el pago.', 'success')
        return redirect(url_for('cliente.mis_pedidos'))
        
    return redirect(url_for('carrito.ver_carrito'))
