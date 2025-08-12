from functools import wraps

from flask import jsonify, render_template, request, flash, redirect, url_for, session, Blueprint
from dotenv import load_dotenv
from app.admin import bd

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

expert_bp = Blueprint('expert', __name__, template_folder='templates')

load_dotenv()


@expert_bp.before_request
def before_request():
    allowed_routes = ['login', 'register', 'static', 'api_index']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('auth.login'))



# Декоратор для проверки прав
def expert_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'expert':
            return jsonify({
                "error": f"access denied {session['role']}"
            }), 403
        return f(*args, **kwargs)
    return decorated_function



@expert_bp.route('/', methods=['GET'])
@expert_required
def index():
    return render_template('expert/index.html')



