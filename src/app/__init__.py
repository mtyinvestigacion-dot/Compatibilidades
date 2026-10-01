from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from config import Config

db = SQLAlchemy()


def _migrar_columna_resultado():
    inspector = db.inspect(db.engine)
    columnas = [c['name'] for c in inspector.get_columns('compatibilidades')]
    if 'resultado' not in columnas:
        db.session.execute(
            text("ALTER TABLE compatibilidades ADD COLUMN resultado VARCHAR(20) NOT NULL DEFAULT 'exitosa'")
        )
        db.session.commit()


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    db.init_app(app)

    from app.auth import login_manager
    login_manager.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template('403.html'), 403

    with app.app_context():
        db.create_all()
        _migrar_columna_resultado()

    return app
