"""
Crea el primer usuario admin del Sistema de Compatibilidades.

Uso (desde la raiz del proyecto):
    python scripts/seed_admin.py

Es seguro correrlo varias veces: si ya existe un admin activo, no hace nada.
"""
import os
import sys

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
sys.path.insert(0, SRC_DIR)

from app import create_app, db
from app.models import Usuario


def main():
    app = create_app()
    with app.app_context():
        admin_existente = Usuario.query.filter_by(rol='admin', activo=True).first()
        if admin_existente:
            print(f'Ya existe un admin activo: "{admin_existente.username}". No se creo ninguno nuevo.')
            return

        print('Creando el primer usuario administrador.')
        username = input('Usuario: ').strip()
        if not username:
            print('El usuario no puede estar vacio.')
            return
        if Usuario.query.filter_by(username=username).first():
            print(f'Ya existe un usuario con el nombre "{username}".')
            return

        # Se usa input() normal (no getpass) porque en varias terminales de Windows
        # (Git Bash, VS Code, etc.) el prompt oculto de getpass se cuelga y no
        # acepta lo que escribes. La contraseña se vera en pantalla al teclearla,
        # aceptable porque este script solo lo corre Marco una vez, en su propia PC.
        password = input('Contraseña (se vera en pantalla): ')
        password_confirm = input('Confirmar contraseña: ')
        if len(password) < 6:
            print('La contraseña debe tener al menos 6 caracteres.')
            return
        if password != password_confirm:
            print('Las contraseñas no coinciden.')
            return

        admin = Usuario(username=username, rol='admin')
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f'Usuario admin "{username}" creado correctamente.')


if __name__ == '__main__':
    main()
