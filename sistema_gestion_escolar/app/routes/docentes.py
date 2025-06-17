from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.docente import Docente
from app.models.usuario import Usuario
from app.utils.decorators import rol_required

docentes_bp = Blueprint('docentes', __name__)

@docentes_bp.route('/docentes')
@rol_required('admin')
def listar_docentes():
    docentes = Docente.obtener_todos_con_usuario_info() # Method needed for listing
    return render_template('docentes/listar.html', docentes=docentes)

# Creating a docente might be handled via admin.gestionar_usuarios_post in the consolidated admin dashboard
# but if you need a dedicated page:
@docentes_bp.route('/docentes/crear', methods=['GET', 'POST'])
@rol_required('admin')
def crear_docente():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # This should be handled by Usuario creation
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        correo = request.form['correo']
        
        if Usuario.obtener_por_username(username):
            flash('El nombre de usuario ya existe.', 'warning')
            return render_template('docentes/crear.html')
        if Usuario.obtener_por_correo(correo):
            flash('El correo electrónico ya está registrado.', 'warning')
            return render_template('docentes/crear.html')

        try:
            Usuario.crear(username, password, 'docente')
            Docente.crear(username=username, nombres=nombres, apellidos=apellidos, dni=dni, correo=correo)
            flash('Docente creado exitosamente.', 'success')
            return redirect(url_for('docentes.listar_docentes'))
        except Exception as e:
            Usuario.eliminar(username) # Rollback if docente creation fails
            flash(f'Error al crear docente: {e}', 'danger')
            
    return render_template('docentes/crear.html')

@docentes_bp.route('/docentes/editar/<string:username>', methods=['GET', 'POST'])
@rol_required('admin')
def editar_docente(username):
    docente = Docente.obtener_por_username(username)
    if not docente:
        flash('Docente no encontrado.', 'danger')
        return redirect(url_for('docentes.listar_docentes'))

    if request.method == 'POST':
        new_username = request.form['username']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        dni = request.form['dni']
        correo = request.form['correo']
        
        try:
            # Update Usuario first if username changed
            if username != new_username:
                Usuario.actualizar_username(username, new_username) # Need a method for username change
            
            Docente.actualizar(new_username, nombres, apellidos, dni, correo)
            flash('Docente actualizado exitosamente.', 'success')
            return redirect(url_for('docentes.listar_docentes'))
        except Exception as e:
            flash(f'Error al actualizar docente: {e}', 'danger')
            
    return render_template('docentes/editar.html', docente=docente)

@docentes_bp.route('/docentes/eliminar/<string:username>', methods=['POST'])
@rol_required('admin')
def eliminar_docente(username):
    try:
        Docente.eliminar(username) # This method should also delete the associated Usuario
        flash('Docente eliminado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar docente: {e}', 'danger')
    return redirect(url_for('docentes.listar_docentes'))