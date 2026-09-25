from datetime import datetime

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.auth import admin_required
from app.models import ROLES, Compatibilidad, Usuario

main = Blueprint('main', __name__)

RUTAS_SIN_LOGIN = ('main.login', 'static', 'main.static')


@main.before_request
def require_login():
    if request.endpoint in RUTAS_SIN_LOGIN:
        return
    if not current_user.is_authenticated:
        return redirect(url_for('main.login', next=request.path))


def _validar_compatibilidad(form):
    errores = []
    if not form.get('panel_reemplazo', '').strip():
        errores.append('El panel de reemplazo es obligatorio.')
    if not form.get('marca_tv', '').strip():
        errores.append('La marca de la TV es obligatoria.')
    if not form.get('modelo_tv', '').strip():
        errores.append('El modelo de la TV es obligatorio.')
    if not form.get('panel_original_tv', '').strip():
        errores.append('El panel original de la TV es obligatorio.')
    return errores


# --- Auth -------------------------------------------------------------

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        usuario = Usuario.query.filter_by(username=username, activo=True).first()
        if usuario and usuario.check_password(password):
            login_user(usuario)
            next_url = request.args.get('next')
            return redirect(next_url or url_for('main.index'))
        flash('Usuario o contraseña incorrectos.', 'error')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# --- Compatibilidades ---------------------------------------------------

@main.route('/')
def index():
    q = request.args.get('q', '').strip()
    marca = request.args.get('marca', '').strip()

    query = Compatibilidad.query.filter_by(activo=True)
    if marca:
        query = query.filter(Compatibilidad.marca_tv == marca)
    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Compatibilidad.panel_reemplazo.ilike(like),
                Compatibilidad.marca_tv.ilike(like),
                Compatibilidad.modelo_tv.ilike(like),
                Compatibilidad.panel_original_tv.ilike(like),
            )
        )
    compatibilidades = query.order_by(Compatibilidad.marca_tv, Compatibilidad.modelo_tv).all()

    marcas = [
        m[0] for m in
        db.session.query(Compatibilidad.marca_tv).filter_by(activo=True).distinct().order_by(Compatibilidad.marca_tv)
    ]

    return render_template(
        'compatibilidades/listar.html',
        compatibilidades=compatibilidades,
        q=q,
        marca=marca,
        marcas=marcas,
    )


@main.route('/compatibilidades/nueva', methods=['GET', 'POST'])
@admin_required
def nueva_compatibilidad():
    if request.method == 'POST':
        errores = _validar_compatibilidad(request.form)
        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('compatibilidades/form.html', compatibilidad=None, valores=request.form)

        compatibilidad = Compatibilidad(
            panel_reemplazo=request.form.get('panel_reemplazo').strip(),
            descripcion_panel=request.form.get('descripcion_panel', '').strip() or None,
            marca_tv=request.form.get('marca_tv').strip().upper(),
            modelo_tv=request.form.get('modelo_tv').strip(),
            panel_original_tv=request.form.get('panel_original_tv').strip(),
            pulgada=request.form.get('pulgada', '').strip() or None,
            observaciones=request.form.get('observaciones', '').strip() or None,
            creado_por_id=current_user.id,
        )
        db.session.add(compatibilidad)
        db.session.commit()
        flash('Compatibilidad guardada correctamente.', 'success')
        return redirect(url_for('main.index'))

    return render_template('compatibilidades/form.html', compatibilidad=None, valores={})


@main.route('/compatibilidades/<int:compat_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_compatibilidad(compat_id):
    compatibilidad = Compatibilidad.query.get_or_404(compat_id)

    if request.method == 'POST':
        errores = _validar_compatibilidad(request.form)
        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('compatibilidades/form.html', compatibilidad=compatibilidad, valores=request.form)

        compatibilidad.panel_reemplazo = request.form.get('panel_reemplazo').strip()
        compatibilidad.descripcion_panel = request.form.get('descripcion_panel', '').strip() or None
        compatibilidad.marca_tv = request.form.get('marca_tv').strip().upper()
        compatibilidad.modelo_tv = request.form.get('modelo_tv').strip()
        compatibilidad.panel_original_tv = request.form.get('panel_original_tv').strip()
        compatibilidad.pulgada = request.form.get('pulgada', '').strip() or None
        compatibilidad.observaciones = request.form.get('observaciones', '').strip() or None
        compatibilidad.modificado_por_id = current_user.id
        compatibilidad.fecha_modificacion = datetime.utcnow()
        db.session.commit()
        flash('Compatibilidad actualizada correctamente.', 'success')
        return redirect(url_for('main.index'))

    valores = {
        'panel_reemplazo': compatibilidad.panel_reemplazo,
        'descripcion_panel': compatibilidad.descripcion_panel or '',
        'marca_tv': compatibilidad.marca_tv,
        'modelo_tv': compatibilidad.modelo_tv,
        'panel_original_tv': compatibilidad.panel_original_tv,
        'pulgada': compatibilidad.pulgada or '',
        'observaciones': compatibilidad.observaciones or '',
    }
    return render_template('compatibilidades/form.html', compatibilidad=compatibilidad, valores=valores)


@main.route('/compatibilidades/<int:compat_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_compatibilidad(compat_id):
    compatibilidad = Compatibilidad.query.get_or_404(compat_id)
    compatibilidad.activo = False
    db.session.commit()
    flash('Compatibilidad eliminada.', 'success')
    return redirect(url_for('main.index'))


@main.route('/api/marcas')
def api_marcas():
    marcas = [m[0] for m in db.session.query(Compatibilidad.marca_tv).filter_by(activo=True).distinct()]
    return jsonify(sorted(marcas))


@main.route('/api/modelos')
def api_modelos():
    modelos = [m[0] for m in db.session.query(Compatibilidad.modelo_tv).filter_by(activo=True).distinct()]
    return jsonify(sorted(modelos))


# --- Usuarios (solo admin) ----------------------------------------------

@main.route('/usuarios')
@admin_required
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.username).all()
    return render_template('usuarios/listar.html', usuarios=usuarios)


@main.route('/usuarios/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        rol = request.form.get('rol', 'viewer')

        errores = []
        if not username:
            errores.append('El usuario es obligatorio.')
        elif Usuario.query.filter_by(username=username).first():
            errores.append('Ya existe un usuario con ese nombre.')
        if len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        if password != password_confirm:
            errores.append('Las contraseñas no coinciden.')
        if rol not in ROLES:
            errores.append('Rol inválido.')

        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('usuarios/form.html', form=request.form)

        usuario = Usuario(username=username, rol=rol)
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        flash(f'Usuario "{username}" creado correctamente.', 'success')
        return redirect(url_for('main.listar_usuarios'))

    return render_template('usuarios/form.html', form=None)


@main.route('/usuarios/<int:usuario_id>/toggle', methods=['POST'])
@admin_required
def toggle_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.id == current_user.id:
        flash('No puedes desactivar tu propia cuenta.', 'error')
        return redirect(url_for('main.listar_usuarios'))

    usuario.activo = not usuario.activo
    db.session.commit()
    estado = 'activado' if usuario.activo else 'desactivado'
    flash(f'Usuario "{usuario.username}" {estado}.', 'success')
    return redirect(url_for('main.listar_usuarios'))


@main.route('/usuarios/<int:usuario_id>/reset-password', methods=['GET', 'POST'])
@admin_required
def reset_password(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == 'POST':
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        errores = []
        if len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres.')
        if password != password_confirm:
            errores.append('Las contraseñas no coinciden.')

        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('usuarios/reset_password.html', usuario=usuario)

        usuario.set_password(password)
        db.session.commit()
        flash(f'Contraseña de "{usuario.username}" actualizada.', 'success')
        return redirect(url_for('main.listar_usuarios'))

    return render_template('usuarios/reset_password.html', usuario=usuario)
