import os
from dotenv import load_dotenv
from flask import Flask
from datetime import datetime

load_dotenv()

def datetimeformat(value, format='%d.%m.%Y %H:%M'):
    if value is None:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

def dateformat(value, format='%d.%m.%Y'):
    if value is None:
        return ""
    if isinstance(value, str):
        value = datetime.fromisoformat(value).date()
    return value.strftime(format)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('API_SECRET_KEY')

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['dateformat'] = dateformat

    # Регистрация blueprint'ов
    register_blueprints(app)

    return app




def register_blueprints(app):
    from CRM_LEAS.app.auth.routes import auth_bp
    from CRM_LEAS.app.admin.main import admin_bp
    from CRM_LEAS.app.manager.main import manager_bp
    from CRM_LEAS.app.expert.main import expert_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(expert_bp, url_prefix='/expert')