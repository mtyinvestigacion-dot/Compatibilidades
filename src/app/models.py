from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

ROLES = ('admin', 'viewer')


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='viewer')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        return self.activo

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M') if self.fecha_creacion else None,
        }


class Compatibilidad(db.Model):
    __tablename__ = 'compatibilidades'

    id = db.Column(db.Integer, primary_key=True)

    # Panel de reemplazo (la parte)
    panel_reemplazo = db.Column(db.String(150), nullable=False, index=True)
    descripcion_panel = db.Column(db.String(255))

    # TV completo con la que es compatible
    marca_tv = db.Column(db.String(100), nullable=False, index=True)
    modelo_tv = db.Column(db.String(150), nullable=False, index=True)
    panel_original_tv = db.Column(db.String(150), nullable=False)
    pulgada = db.Column(db.String(20))

    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)

    creado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    modificado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_modificacion = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'panel_reemplazo': self.panel_reemplazo,
            'descripcion_panel': self.descripcion_panel,
            'marca_tv': self.marca_tv,
            'modelo_tv': self.modelo_tv,
            'panel_original_tv': self.panel_original_tv,
            'pulgada': self.pulgada,
            'observaciones': self.observaciones,
        }
