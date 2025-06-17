# app/routes/estudiante.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.estudiante import Estudiante

def estudiante_required(f):
    @login_required
    def wrap(*args, **kwargs):
        if not hasattr(current_user, 'rol') or current_user.rol != 'estudiante':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('dashboard_bp.inicio'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

estudiante_bp = Blueprint('estudiante_bp', __name__, template_folder='../templates/estudiante')

@estudiante_bp.route('/estudiante/inicio')
@estudiante_required
def estudiante_dashboard():
    estudiante_data = Estudiante.find_by_username(current_user.username)
    return render_template('estudiante/dashboard.html', estudiante=estudiante_data)

# --- Rutas de Gestión del Estudiante (ejemplos) ---

@estudiante_bp.route('/estudiante/mis_cursos')
@estudiante_required
def mis_cursos():
    return render_template('estudiante/mis_cursos.html', cursos=[])

@estudiante_bp.route('/estudiante/mis_notas')
@estudiante_required
def mis_notas():
    return render_template('estudiante/mis_notas.html', notas=[])