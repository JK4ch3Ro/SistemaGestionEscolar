from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash # Asegúrate de importar generate_password_hash también
from app.models.usuario import Usuario

auth_bp = Blueprint('auth_bp', __name__, template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Si el usuario ya está autenticado, redirigirlo a su dashboard
        return redirect(url_for('dashboard_bp.inicio')) # <--- ¡CAMBIO AQUÍ!

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.find_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            # Redirigir al dashboard general, que luego redirigirá según el rol
            return redirect(url_for('dashboard_bp.inicio')) # <--- ¡CAMBIO AQUÍ!
        else:
            flash('Credenciales incorrectas. Por favor, inténtelo de nuevo.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth_bp.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Si el usuario ya está autenticado, redirigirlo a su dashboard
        return redirect(url_for('dashboard_bp.inicio')) # <--- ¡CAMBIO AQUÍ! (aunque no era el error principal, es consistente)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = request.form.get('rol', 'estudiante') # Por defecto, un nuevo registro es estudiante
        
        # Validaciones básicas
        if not username or not password:
            flash('Por favor, complete todos los campos.', 'danger')
            return render_template('register.html')
        
        if Usuario.find_by_username(username):
            flash('El nombre de usuario ya existe. Por favor, elija otro.', 'danger')
            return render_template('register.html')

        # NOTA: En tu modelo Usuario, el método para crear es 'crear', no 'create_user'.
        # Asegúrate de usar el correcto aquí, de lo contrario esto fallará.
        # Lo más probable es que necesites:
        # new_user = Usuario.crear(username, password, rol)
        # Esto porque 'crear' ya hashea la contraseña que le pasas.
        
        # Si tu Usuario.crear ya hashea, no necesitas generate_password_hash(password) aquí.
        # Si tu Usuario.crear espera el hash, entonces sí.
        # Basado en lo que hemos trabajado, Usuario.crear espera la contraseña en texto plano.
        
        # hashed_password = generate_password_hash(password) # Probablemente no necesario si Usuario.crear lo hace

        try:
            new_user = Usuario.crear(username, password, rol) # <--- Reemplazar con esto si Usuario.crear hashea
            if new_user:
                flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('auth_bp.login'))
            else:
                flash('Error al registrar el usuario. Por favor, inténtelo de nuevo.', 'danger')
        except Exception as e:
            flash(f'Error al registrar el usuario: {e}', 'danger')
            return render_template('register.html')

    return render_template('register.html')