from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_login import current_user, login_required # Importar current_user y login_required de flask_login

# No necesitamos rol_required aquí, ya que current_user.rol nos da el rol
# Si 'app.utils.decorators.rol_required' no es estrictamente necesario para la lógica de inicio,
# y la validación de roles se hace con current_user.rol, podemos omitirlo para simplificar
# y evitar un posible error si no está definido o hay un problema de importación.
# Si lo necesitas en otras rutas, asegúrate de que esté correctamente implementado.


# Asegúrate de que el nombre del blueprint coincida con cómo lo registraste en __init__.py
# En tu __init__.py lo tienes como 'dashboard_bp'
dashboard_bp = Blueprint('dashboard_bp', __name__) # <--- Cambiado de 'dashboard' a 'dashboard_bp'

@dashboard_bp.route('/')

@login_required # Usa login_required para asegurar que el usuario esté autenticado
def inicio():
    # current_user ya nos da acceso al usuario autenticado, no necesitamos verificar session['usuario']
    # login_required ya se encarga de redirigir si no hay sesión
    
    # current_user.rol viene de tu modelo Usuario y tu user_loader
    rol = current_user.rol 
    
    # Redirigir al dashboard específico del rol usando los NOMBRES CORRECTOS de BLUEPRINT y FUNCIONES
    if rol == 'admin':
        # Blueprint: admin_bp, Función: admin_dashboard
        return redirect(url_for('admin_bp.admin_dashboard'))
    elif rol == 'docente':
        # Blueprint: docente_bp, Función: docente_dashboard
        return redirect(url_for('docente_bp.docente_dashboard'))
    elif rol == 'estudiante':
        # Blueprint: estudiante_bp, Función: estudiante_dashboard
        return redirect(url_for('estudiante_bp.estudiante_dashboard'))
    else:
        flash('Tu rol de usuario no tiene un dashboard específico asignado.', 'warning')
        # Si llegamos aquí, el rol no es admin, docente o estudiante.
        # Podrías redirigir a una página de error o un dashboard genérico si lo tienes.
        return render_template('dashboard/index.html', usuario_nombre=current_user.username, rol=rol)

# Esta ruta parece ser un placeholder o una ruta genérica.
# Si realmente necesitas un dashboard index genérico, puedes mantenerlo.
# Si todos los roles deben redirigir a un dashboard específico, puedes eliminarla
# o ajustar su lógica.
@dashboard_bp.route('/dashboard/index')
# Si usas rol_required, asegúrate de que el decorador esté implementado y accesible.
# Por ahora, usaré login_required y una verificación simple.
@login_required 
def dashboard_index():
    if current_user.rol != 'admin': # Puedes hacer la verificación aquí si quieres que solo el admin acceda a esta ruta específica.
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('dashboard_bp.inicio')) # Redirige al inicio principal de dashboards

    return render_template('dashboard/index.html', usuario_nombre=current_user.username, rol=current_user.rol)