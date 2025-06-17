from flask import session, flash, redirect, url_for
from functools import wraps

def login_required(f):
    """
    Decorador para asegurar que un usuario esté logueado.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def rol_required(rol_permitido):
    """
    Decorador para asegurar que el usuario logueado tenga un rol específico.
    Uso: @rol_required('admin') o @rol_required('docente') etc.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'usuario' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'danger')
                return redirect(url_for('auth.login'))
            
            if session.get('rol') != rol_permitido:
                flash(f'No tienes permiso para acceder a esta sección. Se requiere rol: {rol_permitido.capitalize()}', 'danger')
                
                # Podrías redirigir a un dashboard genérico o al login
                if session.get('rol') == 'admin':
                    return redirect(url_for('admin.inicio'))
                elif session.get('rol') == 'docente':
                    return redirect(url_for('profesor.inicio'))
                elif session.get('rol') == 'estudiante':
                    return redirect(url_for('alumno.inicio'))
                else:
                    return redirect(url_for('dashboard.inicio')) # Redirige al dashboard por defecto
            return f(*args, **kwargs)
        return decorated_function
    return decorator