from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


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

    return app
