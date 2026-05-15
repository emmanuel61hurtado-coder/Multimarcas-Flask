from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.cita import Cita
from app.models.moto import Moto
from app.models.repuesto import Repuesto
from app.models.factura import Factura, DetalleFactura
from app.models.pedido import Pedido, DetallePedido

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acceso denegado. Solo administradores.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated

def empleado_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_empleado() or current_user.is_admin()):
            flash('Acceso denegado.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_usuarios = User.query.filter_by(rol='cliente').count()
    total_empleados = User.query.filter_by(rol='empleado').count()
    total_citas = Cita.query.count()
    citas_pendientes = Cita.query.filter_by(estado='pendiente').count()
    motos = Moto.query.count()
    repuestos = Repuesto.query.count()
    total_pedidos = Pedido.query.count()
    total_facturas = Factura.query.count()

    try:
        citas_recientes = Cita.query.order_by(Cita.creado_en.desc()).limit(10).all()
    except:
        citas_recientes = Cita.query.limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_usuarios=total_usuarios,
        total_empleados=total_empleados,
        total_citas=total_citas,
        citas_pendientes=citas_pendientes,
        motos=motos,
        repuestos=repuestos,
        total_pedidos=total_pedidos,
        total_facturas=total_facturas,
        citas_recientes=citas_recientes
    )

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    query = request.args.get('q', '').strip()
    if query:
        search = f"%{query}%"
        users = User.query.filter(
            User.rol == 'cliente',
            (User.nombre_completo.ilike(search)) | 
            (User.username.ilike(search)) | 
            (User.email.ilike(search))
        ).all()
    else:
        users = User.query.filter_by(rol='cliente').all()
    
    return render_template('admin/usuarios.html', users=users, search_query=query)

@admin_bp.route('/empleados')
@login_required
@admin_required
def empleados():
    query = request.args.get('q', '').strip()
    if query:
        search = f"%{query}%"
        empleados = User.query.filter(
            User.rol.in_(['empleado', 'admin']),
            (User.nombre_completo.ilike(search)) | 
            (User.username.ilike(search)) | 
            (User.email.ilike(search))
        ).all()
    else:
        empleados = User.query.filter(User.rol.in_(['empleado', 'admin'])).all()
    
    return render_template('admin/empleados.html', empleados=empleados, search_query=query)

@admin_bp.route('/empleados/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_empleado():
    if request.method == 'POST':
        nombre = request.form.get('nombre_completo', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        password = request.form.get('password', '')

        if not all([nombre, username, email, password]):
            flash('Todos los campos son obligatorios.', 'danger')
            return render_template('admin/nuevo_empleado.html')

        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'danger')
            return render_template('admin/nuevo_empleado.html')

        if User.query.filter_by(email=email).first():
            flash('El correo ya existe.', 'danger')
            return render_template('admin/nuevo_empleado.html')

        emp = User(
            nombre_completo=nombre,
            username=username,
            email=email,
            telefono=telefono,
            rol='empleado',
            password=generate_password_hash(password)
        )

        db.session.add(emp)
        db.session.commit()
        flash('Empleado registrado exitosamente.', 'success')
        return redirect(url_for('admin.empleados'))

    return render_template('admin/nuevo_empleado.html')

@admin_bp.route('/usuario/<int:uid>/rol', methods=['POST'])
@login_required
@admin_required
def cambiar_rol(uid):
    user = User.query.get_or_404(uid)
    nuevo_rol = request.form.get('rol')

    if nuevo_rol in ['cliente', 'empleado', 'admin'] and user.username != 'admin':
        user.rol = nuevo_rol
        db.session.commit()
        flash(f'Rol de {user.nombre_completo} actualizado a {nuevo_rol}.', 'success')

    return redirect(request.referrer or url_for('admin.usuarios'))

@admin_bp.route('/usuario/<int:uid>/toggle')
@login_required
@admin_required
def toggle_usuario(uid):
    user = User.query.get_or_404(uid)

    if user.username != 'admin':
        user.activo = not user.activo
        db.session.commit()
        estado = 'activado' if user.activo else 'desactivado'
        flash(f'Usuario {estado} exitosamente.', 'success')

    return redirect(request.referrer or url_for('admin.usuarios'))

@admin_bp.route('/usuario/<int:uid>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(uid):
    user = User.query.get_or_404(uid)

    if user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
        flash('Usuario eliminado.', 'success')

    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/citas')
@login_required
@empleado_required
def citas():
    query = request.args.get('q', '').strip()
    fecha_inicio = request.args.get('fecha_inicio', '').strip()
    fecha_fin = request.args.get('fecha_fin', '').strip()

    citas_query = Cita.query

    if query:
        search = f"%{query}%"
        # Hacemos join con User y Moto para poder buscar por esos campos
        citas_query = citas_query.join(User).join(Moto).filter(
            (User.nombre_completo.ilike(search)) |
            (Moto.placa.ilike(search)) |
            (Cita.tipo_servicio.ilike(search)) |
            (Cita.estado.ilike(search))
        )
        
    if fecha_inicio:
        try:
            start_date = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            citas_query = citas_query.filter(Cita.fecha >= start_date)
        except ValueError:
            pass

    if fecha_fin:
        try:
            # Añadimos 1 día y restamos 1 segundo para incluir todo el día final (hasta las 23:59:59)
            end_date = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            citas_query = citas_query.filter(Cita.fecha <= end_date)
        except ValueError:
            pass

    todas = citas_query.order_by(Cita.fecha.desc()).all()
    
    return render_template('admin/citas.html', citas=todas, search_query=query, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

@admin_bp.route('/cita/<int:cid>/estado', methods=['POST'])
@login_required
@empleado_required
def cambiar_estado_cita(cid):
    cita = Cita.query.get_or_404(cid)
    nuevo_estado = request.form.get('estado')
    total = request.form.get('total')

    if nuevo_estado in ['pendiente', 'confirmada', 'completada', 'cancelada']:
        cita.estado = nuevo_estado

        try:
            if total:
                cita.total = float(total)
        except:
            pass

        db.session.commit()
        flash('Cita actualizada.', 'success')

    return redirect(url_for('admin.citas'))

@admin_bp.route('/cita/<int:cid>/editar', methods=['POST'])
@login_required
@empleado_required
def editar_cita(cid):
    cita = Cita.query.get_or_404(cid)

    fecha_str = request.form.get('fecha')
    hora_str = request.form.get('hora')
    tipo_servicio = request.form.get('tipo_servicio')
    descripcion = request.form.get('descripcion')
    estado = request.form.get('estado')

    if fecha_str and hora_str:
        try:
            cita.fecha = datetime.strptime(f"{fecha_str} {hora_str}", '%Y-%m-%d %H:%M')
        except:
            flash('Fecha u hora inválida.', 'danger')
            return redirect(url_for('admin.citas'))

    if tipo_servicio:
        cita.tipo_servicio = tipo_servicio
    if descripcion is not None:
        cita.descripcion = descripcion
    if estado in ['pendiente', 'confirmada', 'completada', 'cancelada']:
        cita.estado = estado

    db.session.commit()
    flash('Cita actualizada exitosamente.', 'success')
    return redirect(url_for('admin.citas'))

@admin_bp.route('/motos')
@login_required
@admin_required
def motos():
    query = request.args.get('q', '').strip()
    if query:
        search = f"%{query}%"
        todas_motos = Moto.query.join(User).filter(
            (Moto.placa.ilike(search)) | 
            (Moto.marca.ilike(search)) | 
            (Moto.modelo.ilike(search)) |
            (User.nombre_completo.ilike(search))
        ).all()
    else:
        todas_motos = Moto.query.all()
    
    return render_template('admin/motos.html', motos=todas_motos, search_query=query)

@admin_bp.route('/facturas')
@login_required
@admin_required
def facturas():
    query = request.args.get('q', '').strip()
    if query:
        search = f"%{query}%"
        # Buscar por número de factura, nombre de cliente o placa de moto
        todas_facturas = Factura.query.join(User).outerjoin(Moto).filter(
            (Factura.numero.ilike(search)) |
            (User.nombre_completo.ilike(search)) |
            (Moto.placa.ilike(search))
        ).order_by(Factura.fecha.desc()).all()
    else:
        todas_facturas = Factura.query.order_by(Factura.fecha.desc()).all()
        
    hoy = datetime.now().date()
    
    categorias = {
        'Hoy': [],
        'Esta Semana': [],
        'Este Mes': [],
        'Mes Pasado': [],
        'Anteriores': []
    }
    
    for f in todas_facturas:
        f_date = f.fecha.date() if isinstance(f.fecha, datetime) else f.fecha
        delta_days = (hoy - f_date).days
        
        if delta_days == 0:
            categorias['Hoy'].append(f)
        elif 0 < delta_days <= 7:
            categorias['Esta Semana'].append(f)
        elif f_date.month == hoy.month and f_date.year == hoy.year:
            categorias['Este Mes'].append(f)
        elif (f_date.year == hoy.year and f_date.month == hoy.month - 1) or \
             (f_date.year == hoy.year - 1 and hoy.month == 1 and f_date.month == 12):
            categorias['Mes Pasado'].append(f)
        else:
            categorias['Anteriores'].append(f)
            
    # Removemos el filtrado de categorías vacías para que siempre aparezcan las tarjetas (mostrando 0 si no hay)
    
    return render_template('admin/facturas.html', facturas=todas_facturas, categorias=categorias, search_query=query)

@admin_bp.route('/factura/nueva')
@login_required
@admin_required
def nueva_factura():
    cita_id = request.args.get('cita_id')
    cita_previa = None
    if cita_id:
        cita_previa = Cita.query.get(cita_id)
        
    usuarios = User.query.filter_by(rol='cliente').all()
    empleados = User.query.filter(User.rol.in_(['empleado', 'admin'])).all()
    motos = Moto.query.all()
    repuestos = Repuesto.query.all()
    
    ultima = Factura.query.order_by(Factura.id.desc()).first()
    nuevo_num = f"FAC-{str(ultima.id + 1).zfill(3)}" if ultima else "FAC-001"
    
    return render_template('admin/nueva_factura.html', 
                           usuarios=usuarios, 
                           empleados=empleados,
                           motos=motos, 
                           repuestos=repuestos,
                           sugerido=nuevo_num,
                           cita_previa=cita_previa)

@admin_bp.route('/factura/guardar', methods=['POST'])
@login_required
@admin_required
def guardar_factura():
    data = request.form
    cliente_id = data.get('cliente_id')
    empleado_id = data.get('empleado_id')
    moto_id = data.get('moto_id')
    cita_id = data.get('cita_id') # Campo oculto nuevo
    numero = data.get('numero')
    metodo = data.get('metodo_pago')
    
    descripciones = request.form.getlist('desc[]')
    cantidades = request.form.getlist('cant[]')
    precios = request.form.getlist('precio[]')
    
    nueva = Factura(
        numero=numero,
        user_id=cliente_id,
        empleado_id=empleado_id if empleado_id else None,
        moto_id=moto_id if moto_id else None,
        cita_id=cita_id if cita_id else None,
        metodo_pago=metodo
    )
    
    # CAPTURAR MANO DE OBRA SEGURO
    mano_obra_str = data.get('mano_obra', '0').strip()
    try:
        mano_obra = float(mano_obra_str) if mano_obra_str else 0.0
    except ValueError:
        mano_obra = 0.0
        
    subtotal_acum = 0
    
    if mano_obra > 0:
        detalle_mo = DetalleFactura(
            descripcion="Mano de Obra / Servicio Técnico",
            cantidad=1,
            precio_unitario=mano_obra,
            subtotal=mano_obra
        )
        nueva.items.append(detalle_mo)
        subtotal_acum += mano_obra

    for d, c, p in zip(descripciones, cantidades, precios):
        if d and str(c).strip() and str(p).strip():
            try:
                cant = int(c)
                prec = float(p)
            except ValueError:
                continue # Saltar si hay error en los números
                
            st = cant * prec
            detalle = DetalleFactura(
                descripcion=d,
                cantidad=cant,
                precio_unitario=prec,
                subtotal=st
            )
            nueva.items.append(detalle)
            subtotal_acum += st
            
            # --- INVENTARIO INTELIGENTE ---
            repuesto_existente = Repuesto.query.filter_by(nombre=d.strip()).first()
            if repuesto_existente:
                # Si existe, descontar del stock (sin bajar de 0 por seguridad)
                repuesto_existente.stock = max(0, repuesto_existente.stock - cant)
            else:
                # Si no existe, crearlo automáticamente
                nuevo_rep = Repuesto(
                    nombre=d.strip(),
                    categoria="Agregado desde Factura",
                    marca="Genérico",
                    precio=prec,
                    stock=0 # Se facturó lo que se agregó, stock queda en 0
                )
                db.session.add(nuevo_rep)
            
    # CALCULAR TOTALES SIN IVA
    nueva.subtotal = subtotal_acum
    nueva.iva = 0.0 # Eliminamos el IVA
    nueva.total = subtotal_acum
    
    # SI VIENE DE UNA CITA, MARCARLA COMO COMPLETADA
    if cita_id and cita_id.strip():
        try:
            cita = Cita.query.get(int(cita_id))
            if cita:
                cita.estado = 'completada'
        except ValueError:
            pass
    
    db.session.add(nueva)
    db.session.commit()
    
    flash(f'Factura {numero} guardada por un total de $ {nueva.total:,.2f}. Cita completada.', 'success')
    return redirect(url_for('admin.facturas'))

@admin_bp.route('/factura/<int:fid>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_factura(fid):
    factura = Factura.query.get_or_404(fid)
    numero = factura.numero
    
    db.session.delete(factura)
    db.session.commit()
    
    flash(f'Factura {numero} eliminada exitosamente del sistema.', 'success')
    return redirect(url_for('admin.facturas'))

@admin_bp.route('/pedidos')
@login_required
@admin_required
def pedidos():
    # Obtener todos los pedidos ordenados por fecha
    todos_pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    
    return render_template('admin/pedidos.html', pedidos=todos_pedidos)

@admin_bp.route('/pedido/<int:pid>/estado', methods=['POST'])
@login_required
@admin_required
def actualizar_estado_pedido(pid):
    pedido = Pedido.query.get_or_404(pid)
    nuevo_estado = request.form.get('estado')
    
    if nuevo_estado in ['Pendiente', 'En Preparación', 'Enviado', 'Listo para Retiro', 'Completado', 'Cancelado']:
        pedido.estado = nuevo_estado
        db.session.commit()
        flash(f'Pedido #{pid} actualizado a {nuevo_estado}.', 'success')
        
    return redirect(url_for('admin.pedidos'))

@admin_bp.route('/venta-fisica', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_venta_fisica():
    clientes = User.query.filter_by(rol='cliente').order_by(User.nombre_completo).all()
    repuestos = Repuesto.query.order_by(Repuesto.nombre).all()

    if request.method == 'POST':
        user_id_str = request.form.get('user_id', '').strip()
        nombre_fisico = request.form.get('nombre_cliente_fisico', '').strip()
        metodo_pago = request.form.get('metodo_pago', 'efectivo')

        repuesto_ids = request.form.getlist('repuesto_id[]')
        cantidades = request.form.getlist('cantidad[]')

        # Si no se seleccionó cliente con cuenta, usar el admin como titular
        if user_id_str:
            uid = int(user_id_str)
        else:
            # Usar el admin actual como titular del pedido
            uid = current_user.id

        total = 0
        items_venta = []
        for rid, cant_str in zip(repuesto_ids, cantidades):
            if not rid:
                continue
            rep = Repuesto.query.get(int(rid))
            cant = max(1, int(cant_str or 1))
            if rep:
                subtotal = rep.precio * cant
                total += subtotal
                items_venta.append((rep, cant, subtotal))

        if not items_venta:
            flash('Debes agregar al menos un repuesto.', 'danger')
            return render_template('admin/venta_fisica.html', clientes=clientes, repuestos=repuestos)

        nuevo_pedido = Pedido(
            user_id=uid,
            metodo_entrega='Taller',
            origen='Físico',
            nombre_cliente_fisico=nombre_fisico or None,
            telefono_contacto='',
            estado='Completado',
            total=total
        )

        db.session.add(nuevo_pedido)

        for rep, cant, st in items_venta:
            detalle = DetallePedido(
                pedido=nuevo_pedido,
                repuesto_id=rep.id,
                cantidad=cant,
                precio_unitario=rep.precio,
                subtotal=st
            )
            db.session.add(detalle)
            # Descontar stock automáticamente (el admin registró la venta que ya ocurrió)
            rep.stock = max(0, rep.stock - cant)

        db.session.commit()
        flash(f'Venta física registrada por $ {total:,.0f}. Stock actualizado.', 'success')
        return redirect(url_for('admin.pedidos'))

    return render_template('admin/venta_fisica.html', clientes=clientes, repuestos=repuestos)