from functools import wraps

from flask import abort
from flask_login import LoginManager, current_user

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Inicia sesión para continuar.'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario
    usuario = Usuario.query.get(int(user_id))
    if usuario and usuario.activo:
        return usuario
    return None


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper
