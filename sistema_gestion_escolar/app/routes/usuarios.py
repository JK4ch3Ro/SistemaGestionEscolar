from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.usuario import Usuario

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
def index():
    usuarios = Usuario.obtener_todos()
    # La plantilla para listar usuarios está en 'admin/usuarios.html'
    return render_template('admin/usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']

        if Usuario.existe_username(username):
            flash('El nombre de usuario ya existe. Por favor elige otro.', 'danger')
            # Redirige a la misma ruta para mostrar el formulario con el mensaje de error
            return redirect(url_for('usuarios.nuevo'))

        try:
            Usuario.crear(username, password, rol)
            flash('Usuario creado correctamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            flash(f'Error al crear el usuario: {e}', 'danger')
            return redirect(url_for('usuarios.nuevo'))

    # La plantilla para el formulario de nuevo usuario está en 'admin/usuarios.html'
    # También podría ser una sección específica dentro de ella si solo muestra el formulario.
    return render_template('admin/usuarios.html')


@usuarios_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    usuario = Usuario.obtener_por_id(id)
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('usuarios.index'))

    if request.method == 'POST':
        # Validar si el nuevo username ya existe y no es el mismo del usuario que se edita
        nuevo_username = request.form['username']
        if nuevo_username != usuario.username and Usuario.existe_username(nuevo_username):
            flash('El nuevo nombre de usuario ya existe. Por favor elige otro.', 'danger')
            return redirect(url_for('usuarios.editar', id=id))

        try:
            usuario.username = nuevo_username
            usuario.password = request.form['password'] # Considera no actualizar la contraseña aquí directamente o hashear
            usuario.rol = request.form['rol']
            usuario.actualizar()
            flash('Usuario actualizado correctamente.', 'success')
            return redirect(url_for('usuarios.index'))
        except Exception as e:
            flash(f'Error al actualizar el usuario: {e}', 'danger')
            return redirect(url_for('usuarios.editar', id=id))

    # La plantilla para el formulario de edición de usuario está en 'admin/usuarios.html'
    # Pasamos el objeto 'usuario' para precargar los campos del formulario.
    return render_template('admin/usuarios.html', usuario=usuario)

@usuarios_bp.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        Usuario.eliminar(id)
        flash('Usuario eliminado correctamente.', 'info')
    except Exception as e:
        flash(f'Error al eliminar el usuario: {e}', 'danger')
    return redirect(url_for('usuarios.index'))