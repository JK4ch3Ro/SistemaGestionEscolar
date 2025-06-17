from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash 

# Importa todos tus modelos
from app.models.usuario import Usuario
from app.models.docente import Docente
from app.models.estudiante import Estudiante
from app.models.curso import Curso
from app.models.grado import Grado
from app.models.seccion import Seccion
from app.models.matricula import Matricula # Asegúrate de que Matricula esté aquí si la usas

admin_bp = Blueprint('admin_bp', __name__, template_folder='../templates/admin')

# --- Decoradores ---
# Decorador para restringir el acceso solo a administradores
def admin_required(f):
    @login_required
    def wrap(*args, **kwargs):
        if current_user.rol != 'admin':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('dashboard_bp.inicio')) # Asumo 'dashboard_bp' para el inicio del usuario
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__ # Importante para Flask
    return wrap

# --- Rutas del Dashboard de Administración ---
@admin_bp.route('/admin/inicio')
@admin_required
def admin_dashboard():
    # Obtener todos los datos necesarios para las tablas en el dashboard principal
    all_users = Usuario.obtener_todos()
    all_docentes_raw = Docente.obtener_todos()
    all_estudiantes_raw = Estudiante.obtener_todos() # Obtiene estudiantes con solo sus IDs de grado/sección
    all_cursos_raw = Curso.obtener_todos()
    all_grados = Grado.obtener_todos()
    all_secciones = Seccion.obtener_todos()

    # Preparar datos para plantillas con nombres de relaciones
    all_grados_map = {g.id: g.nombre for g in all_grados}
    all_secciones_map = {s.id: s.nombre for s in all_secciones}
    all_docentes_map = {d.username: d for d in all_docentes_raw}

    # --- Preparar estudiantes para la plantilla ---
    estudiantes_for_template = []
    for est in all_estudiantes_raw:
        est_dict = est.to_dict() # Usamos to_dict del modelo Estudiante (asumiendo que lo tiene)
        # CORREGIDO: Accede a 'seccion_id' del objeto Estudiante, no 'id_seccion' (consistente con el modelo)
        est_dict['grado_nombre'] = all_grados_map.get(est.grado_id, 'Desconocido')
        est_dict['seccion_nombre'] = all_secciones_map.get(est.seccion_id, 'Desconocido') 
        estudiantes_for_template.append(est_dict)

    # --- Preparar cursos para la plantilla ---
    cursos_for_template = []
    for curso in all_cursos_raw:
        curso_dict = curso.to_dict() if hasattr(curso, 'to_dict') else curso.__dict__
        if curso.docente_username and curso.docente_username in all_docentes_map:
            docente_obj = all_docentes_map[curso.docente_username]
            curso_dict['docente_nombres'] = docente_obj.nombres
            curso_dict['docente_apellidos'] = docente_obj.apellidos
        else:
            curso_dict['docente_nombres'] = None
            curso_dict['docente_apellidos'] = None
        cursos_for_template.append(curso_dict)

    # --- Usuarios sin perfiles específicos ---
    # Asegúrate de que estos métodos existan en tu modelo Usuario
    usuarios_sin_perfil_docente = Usuario.get_users_without_docente_profile() 
    usuarios_sin_perfil_estudiante = Usuario.get_users_without_estudiante_profile() 

    return render_template('admin/dashboard.html', 
                            users=all_users, 
                            docentes=all_docentes_raw, # Se mantiene raw para usar directamente si no necesitas los nombres completos
                            estudiantes=estudiantes_for_template, # Lista de estudiantes con nombres de grado/sección
                            cursos=cursos_for_template, # Lista de cursos con nombres de docente
                            grados=all_grados, 
                            secciones=all_secciones,
                            # Estos pueden ser redundantes si ya se pasaron como 'grados' y 'secciones'
                            grados_all=all_grados, 
                            secciones_all=all_secciones, 
                            docentes_all=all_docentes_raw, 
                            docentes_disponibles_para_asignar=usuarios_sin_perfil_docente,
                            estudiantes_disponibles_para_asignar=usuarios_sin_perfil_estudiante
                            )

# --- Rutas de Listado Individuales (para enlaces de navegación) ---

@admin_bp.route('/admin/matriculas/listar')
@admin_required
def listar_matriculas():
    all_matriculas_raw = Matricula.obtener_todos()

    all_estudiantes = Estudiante.obtener_todos() 
    all_cursos = Curso.obtener_todos()

    estudiantes_map = {e.username: f"{e.nombres} {e.apellidos}" for e in all_estudiantes} 
    cursos_map = {c.id_curso: c.nombre for c in all_cursos} # Asumo 'id_curso' y 'nombre' en tu modelo Curso

    matriculas_for_template = []
    for mat in all_matriculas_raw:
        mat_dict = mat.to_dict() if hasattr(mat, 'to_dict') else mat.__dict__
        # Asegúrate que el objeto Matricula tiene los atributos 'estudiante_username' y 'curso_id'
        mat_dict['estudiante_nombre_completo'] = estudiantes_map.get(mat.estudiante_username, 'Desconocido') 
        mat_dict['curso_nombre'] = cursos_map.get(mat.curso_id, 'Desconocido') 
        matriculas_for_template.append(mat_dict)

    return render_template('admin/gestionar_matriculas.html', matriculas=matriculas_for_template) 

@admin_bp.route('/admin/usuarios/listar')
@admin_required
def listar_usuarios():
    users = Usuario.obtener_todos()
    return render_template('admin/gestionar_usuarios.html', users=users)

@admin_bp.route('/admin/docentes/listar')
@admin_required
def listar_docentes():
    docentes = Docente.obtener_todos()
    return render_template('docente/listar.html', docentes=docentes) # Asegúrate de que esta plantilla exista

@admin_bp.route('/admin/estudiantes/listar')
@admin_required
def listar_estudiantes():
    estudiantes = Estudiante.obtener_todos()
    all_grados_map = {g.id: g.nombre for g in Grado.obtener_todos()}
    all_secciones_map = {s.id: s.nombre for s in Seccion.obtener_todos()}
    
    estudiantes_for_template = []
    for est in estudiantes:
        est_dict = est.to_dict() # Usamos to_dict del modelo Estudiante (asumiendo que lo tiene)
        # CORREGIDO: Accede a 'seccion_id' del objeto Estudiante, no 'id_seccion' (consistente con el modelo)
        est_dict['grado_nombre'] = all_grados_map.get(est.grado_id, 'Desconocido') 
        est_dict['seccion_nombre'] = all_secciones_map.get(est.seccion_id, 'Desconocido') 
        estudiantes_for_template.append(est_dict)
    
    return render_template('estudiante/listar.html', estudiantes=estudiantes_for_template) # Asegúrate de que esta plantilla exista

@admin_bp.route('/admin/cursos/listar')
@admin_required
def listar_cursos():
    cursos = Curso.obtener_todos()
    all_docentes = Docente.obtener_todos()
    all_docentes_map = {d.username: d for d in all_docentes}
    
    cursos_for_template = []
    for curso in cursos:
        curso_dict = curso.to_dict() if hasattr(curso, 'to_dict') else curso.__dict__
        if curso.docente_username and curso.docente_username in all_docentes_map:
            docente_obj = all_docentes_map[curso.docente_username]
            curso_dict['docente_nombres'] = docente_obj.nombres
            curso_dict['docente_apellidos'] = docente_obj.apellidos
        else:
            curso_dict['docente_nombres'] = None
            curso_dict['docente_apellidos'] = None
        cursos_for_template.append(curso_dict)

    return render_template('cursos/listar.html', cursos=cursos_for_template) # Asegúrate de que esta plantilla exista

@admin_bp.route('/admin/grados/listar')
@admin_required
def listar_grados():
    grados = Grado.obtener_todos()
    return render_template('admin/gestionar_grados.html', grados=grados) 

@admin_bp.route('/admin/secciones/listar')
@admin_required
def listar_secciones():
    secciones = Seccion.obtener_todos()
    return render_template('admin/gestionar_secciones.html', secciones=secciones) 


# --- Rutas POST para gestionar (Crear/Editar/Eliminar) ---

@admin_bp.route('/admin/gestion/usuarios', methods=['POST'])
@admin_required
def gestionar_usuarios_post():
    action = request.form.get('action')
    username = request.form.get('username')
    password = request.form.get('password')
    rol = request.form.get('rol')
    original_username = request.form.get('original_username')

    if action == 'create':
        if not password:
            flash('La contraseña es obligatoria para crear un nuevo usuario.', 'danger')
            return redirect(url_for('admin_bp.admin_dashboard', tab='usuarios'))
        try:
            # Asumo que Usuario.crear maneja el hasheo de la contraseña internamente
            if Usuario.crear(username, password, rol): 
                flash(f'Usuario {username} creado con éxito!', 'success')
            else:
                flash(f'Error al crear el usuario {username}. Es posible que el username ya exista.', 'danger')
        except Exception as e:
            flash(f'Error al crear usuario: {e}', 'danger')
    elif action == 'edit':
        if original_username and username and rol:
            try:
                hashed_password = None
                if password: # Solo actualiza la contraseña si se proporciona una nueva
                    hashed_password = generate_password_hash(password)
                
                # Asumo que Usuario.actualizar_usuario es el método correcto para actualizar
                if Usuario.actualizar_usuario(original_username, username, rol, hashed_password): 
                    flash(f'Usuario {username} actualizado con éxito!', 'success')
                else:
                    flash(f'Error al actualizar el usuario {username}.', 'danger')
            except Exception as e:
                flash(f'Error al actualizar usuario: {e}', 'danger')
        else:
            flash('Datos incompletos para actualizar usuario.', 'danger')
    elif action == 'delete': 
        try:
            # Asumo que Usuario.eliminar es el método correcto
            if Usuario.eliminar(username): 
                flash(f'Usuario {username} eliminado con éxito.', 'success')
            else:
                flash(f'No se pudo eliminar el usuario {username}.', 'danger')
        except Exception as e:
            flash(f'Error al eliminar usuario: {e}', 'danger')
    else:
        flash('Acción no reconocida para usuarios.', 'danger')
    
    return redirect(url_for('admin_bp.admin_dashboard', tab='usuarios'))

@admin_bp.route('/admin/usuarios/eliminar/<username>')
@admin_required
def eliminar_usuario(username): 
    try:
        if Usuario.eliminar(username): 
            flash(f'Usuario {username} eliminado con éxito.', 'success')
        else:
            flash(f'No se pudo eliminar el usuario {username}.', 'danger')
    except Exception as e:
        flash(f'Error al eliminar usuario: {e}', 'danger')
    return redirect(url_for('admin_bp.admin_dashboard', tab='usuarios'))


@admin_bp.route('/admin/gestion/docentes', methods=['POST'])
@admin_required
def gestionar_docentes_post():
    action = request.form.get('action')
    username = request.form.get('username')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    dni = request.form.get('dni')
    correo = request.form.get('correo')
    original_username = request.form.get('original_username')

    if action == 'create':
        try:
            user = Usuario.find_by_username(username) # Utiliza el método correcto para buscar
            if not user or user.rol != 'docente':
                flash(f'El usuario "{username}" no existe o no tiene el rol de Docente. Cree el usuario primero.', 'danger')
                return redirect(url_for('admin_bp.admin_dashboard', tab='docentes'))
            
            if Docente.crear_docente(username, nombres, apellidos, dni, correo): 
                flash(f'Docente {nombres} {apellidos} creado con éxito!', 'success')
            else:
                flash(f'Error al crear el docente. Es posible que el DNI o correo ya existan, o el usuario ya tiene un perfil de docente.', 'danger')
        except Exception as e:
            flash(f'Error al crear docente: {e}', 'danger')
    elif action == 'edit':
        if original_username and nombres and apellidos and dni and correo:
            try:
                # ASUMO: Docente.update_docente (método estándar, similar a estudiante)
                if Docente.update_docente(original_username, nombres, apellidos, dni, correo): 
                    flash(f'Docente {nombres} {apellidos} actualizado con éxito!', 'success')
                else:
                    flash(f'Error al actualizar el docente. Verifique los datos.', 'danger')
            except Exception as e:
                flash(f'Error al actualizar docente: {e}', 'danger')
        else:
            flash('Datos incompletos para actualizar docente.', 'danger')
    elif action == 'delete': 
        try:
            # ASUMO: Docente.delete_docente (método estándar, similar a estudiante)
            if Docente.delete_docente(username): 
                flash(f'Docente {username} eliminado con éxito.', 'success')
            else:
                flash(f'No se pudo eliminar el docente {username}.', 'danger')
        except Exception as e:
            flash(f'Error al eliminar docente: {e}', 'danger')
    else:
        flash('Acción no reconocida para docentes.', 'danger')
    
    return redirect(url_for('admin_bp.admin_dashboard', tab='docentes'))

@admin_bp.route('/admin/docentes/eliminar/<username>')
@admin_required
def eliminar_docente(username): 
    try:
        # ASUMO: Docente.delete_docente
        if Docente.delete_docente(username): 
            flash(f'Docente {username} eliminado con éxito.', 'success')
        else:
            flash(f'No se pudo eliminar el docente {username}.', 'danger')
    except Exception as e:
        flash(f'Error al eliminar docente: {e}', 'danger')
    return redirect(url_for('admin_bp.admin_dashboard', tab='docentes'))


@admin_bp.route('/admin/gestion/estudiantes', methods=['POST'])
@admin_required
def gestionar_estudiantes_post():
    action = request.form.get('action')
    username = request.form.get('username')
    nombres = request.form.get('nombres')
    apellidos = request.form.get('apellidos')
    dni = request.form.get('dni')
    correo = request.form.get('correo')
    
    # MUY IMPORTANTE: Asegúrate de que el nombre del campo del formulario HTML sea 'grado_id' y 'seccion_id'
    grado_id = request.form.get('grado_id', type=int) 
    seccion_id = request.form.get('seccion_id', type=int) # <--- CORREGIDO: De 'id_seccion' a 'seccion_id'

    original_username = request.form.get('original_username')

    if action == 'create':
        try:
            user = Usuario.find_by_username(username) # Utiliza el método correcto para buscar
            if not user or user.rol != 'estudiante':
                flash(f'El usuario "{username}" no existe o no tiene el rol de Estudiante. Cree el usuario primero.', 'danger')
                return redirect(url_for('admin_bp.admin_dashboard', tab='estudiantes'))

            # Ahora pasas 'seccion_id' a la función, lo cual coincide con el modelo
            if Estudiante.crear_estudiante(username, nombres, apellidos, dni, correo, grado_id, seccion_id): 
                flash(f'Estudiante {nombres} {apellidos} creado con éxito!', 'success')
            else:
                flash(f'Error al crear el estudiante. Es posible que el DNI o correo ya existan, o el usuario ya tiene un perfil de estudiante.', 'danger')
        except Exception as e:
            flash(f'Error al crear estudiante: {e}', 'danger')
    elif action == 'edit':
        # También corrige aquí para el UPDATE
        if original_username and nombres and apellidos and dni and correo and grado_id is not None and seccion_id is not None:
            try:
                # ASUMO: Estudiante.update_estudiante (método que definimos en el modelo Estudiante)
                if Estudiante.update_estudiante(original_username, nombres, apellidos, dni, correo, grado_id, seccion_id): 
                    flash(f'Estudiante {nombres} {apellidos} actualizado con éxito!', 'success')
                else:
                    flash(f'Error al actualizar el estudiante. Verifique los datos.', 'danger')
            except Exception as e:
                flash(f'Error al actualizar estudiante: {e}', 'danger')
        else:
            flash('Datos incompletos para actualizar estudiante.', 'danger')
    elif action == 'delete': 
        try:
            # ASUMO: Estudiante.delete_estudiante (método que definimos en el modelo Estudiante)
            if Estudiante.delete_estudiante(username): 
                flash(f'Estudiante {username} eliminado con éxito.', 'success')
            else:
                flash(f'No se pudo eliminar el estudiante {username}.', 'danger')
        except Exception as e:
            flash(f'Error al eliminar estudiante: {e}', 'danger')
    else:
        flash('Acción no reconocida para estudiantes.', 'danger')
    
    return redirect(url_for('admin_bp.admin_dashboard', tab='estudiantes'))

@admin_bp.route('/admin/estudiantes/eliminar/<username>')
@admin_required
def eliminar_estudiante(username): 
    try:
        # ASUMO: Estudiante.delete_estudiante
        if Estudiante.delete_estudiante(username): 
            flash(f'Estudiante {username} eliminado con éxito.', 'success')
        else:
            flash(f'No se pudo eliminar el estudiante {username}.', 'danger')
    except Exception as e:
        flash(f'Error al eliminar estudiante: {e}', 'danger')
    return redirect(url_for('admin_bp.admin_dashboard', tab='estudiantes'))


@admin_bp.route('/admin/gestion/cursos', methods=['POST'])
@admin_required
def gestionar_cursos_post():
    action = request.form.get('action')
    # La clave del formulario para el ID del curso es 'id', pero lo manejamos como 'id_curso' en el código
    id_curso = request.form.get('id', type=int) 
    nombre = request.form.get('nombre')
    docente_username = request.form.get('docente_username')
    
    if docente_username == '': # Si se envía vacío, significa que no hay docente asignado
        docente_username = None

    if action == 'create':
        try:
            # ASUMO: Curso.crear_curso existe en tu modelo Curso
            if Curso.crear_curso(nombre, docente_username): 
                flash(f'Curso "{nombre}" creado con éxito!', 'success')
            else:
                flash(f'Error al crear el curso "{nombre}". Puede que el nombre ya exista.', 'danger')
        except Exception as e:
            flash(f'Error al crear curso: {e}', 'danger')
    elif action == 'edit':
        if id_curso is not None and nombre: 
            try:
                # ASUMO: Curso.update_curso (método estándar)
                if Curso.update_curso(id_curso, nombre, docente_username): 
                    flash(f'Curso "{nombre}" actualizado con éxito!', 'success')
                else:
                    flash(f'Error al actualizar el curso "{nombre}". Verifique los datos o si el ID existe.', 'danger')
            except Exception as e:
                flash(f'Error al actualizar curso: {e}', 'danger')
        else:
            flash('Datos incompletos para actualizar curso.', 'danger')
    elif action == 'delete': 
        try:
            # ASUMO: Curso.delete_curso (método estándar)
            if Curso.delete_curso(id_curso): 
                flash(f'Curso con ID {id_curso} eliminado con éxito.', 'success')
            else:
                flash(f'No se pudo eliminar el curso con ID {id_curso}.', 'danger')
        except Exception as e:
            flash(f'Error al eliminar curso: {e}', 'danger')
    else:
        flash('Acción no reconocida para cursos.', 'danger')
    
    return redirect(url_for('admin_bp.admin_dashboard', tab='cursos'))

@admin_bp.route('/admin/cursos/eliminar/<int:id_curso>')
@admin_required
def eliminar_curso(id_curso): 
    try:
        # ASUMO: Curso.delete_curso
        if Curso.delete_curso(id_curso): 
            flash(f'Curso con ID {id_curso} eliminado con éxito.', 'success')
        else:
            flash(f'No se pudo eliminar el curso con ID {id_curso}.', 'danger')
    except Exception as e:
        flash(f'Error al eliminar curso: {e}', 'danger')
    return redirect(url_for('admin_bp.admin_dashboard', tab='cursos'))


@admin_bp.route('/admin/gestion/grados', methods=['POST'])
@admin_required
def gestionar_grados_post():
    action = request.form.get('action')
    grado_id = request.form.get('id', type=int) # Usar grado_id para claridad, aunque el formulario use 'id'
    nombre = request.form.get('nombre')

    if action == 'create':
        try:
            # ASUMO: Grado.crear_grado existe en tu modelo Grado
            if Grado.crear_grado(nombre): 
                flash(f'Grado "{nombre}" creado con éxito!', 'success')
            else:
                flash(f'Error al crear el grado "{nombre}". Puede que el nombre ya exista.', 'danger')
        except Exception as e:
            flash(f'Error al crear grado: {e}', 'danger')
    elif action == 'edit':
        if grado_id is not None and nombre: 
            try:
                # ASUMO: Grado.update_grado (método estándar)
                if Grado.update_grado(grado_id, nombre): 
                    flash(f'Grado "{nombre}" actualizado con éxito!', 'success')
                else:
                    flash(f'Error al actualizar el grado "{nombre}". Verifique los datos o si el ID existe.', 'danger')
            except Exception as e:
                flash(f'Error al actualizar grado: {e}', 'danger')
        else:
            flash('Datos incompletos para actualizar grado.', 'danger')
    elif action == 'delete': 
        try:
            # ASUMO: Grado.delete_grado (método estándar)
            if Grado.delete_grado(grado_id): 
                flash(f'Grado con ID {grado_id} eliminado con éxito.', 'success')
            else:
                flash(f'No se pudo eliminar el grado con ID {grado_id}.', 'danger')
        except Exception as e:
            flash(f'Error al eliminar grado: {e}', 'danger')
    else:
        flash('Acción no reconocida para grados.', 'danger')
    
    return redirect(url_for('admin_bp.admin_dashboard', tab='grados'))

@admin_bp.route('/admin/grados/eliminar/<int:id>')
@admin_required
def eliminar_grado(id): # Deja el parámetro 'id' porque así está en la ruta
    try:
        # ASUMO: Grado.delete_grado
        if Grado.delete_grado(id): 
            flash(f'Grado con ID {id} eliminado con éxito.', 'success')
        else:
            flash(f'No se pudo eliminar el grado con ID {id}.', 'danger')
    except Exception as e:
        flash(f'Error al eliminar grado: {e}', 'danger')
    return redirect(url_for('admin_bp.admin_dashboard', tab='grados'))


@admin_bp.route('/admin/gestion/secciones', methods=['POST'])
@admin_required
def gestionar_secciones_post():
    action = request.form.get('action')
    id_seccion_form = request.form.get('id', type=int) # Usar un nombre diferente para evitar confusión
    nombre = request.form.get('nombre')

    if action == 'create':
        try:
            # ASUMO: Seccion.crear_seccion existe en tu modelo Seccion
            if Seccion.crear_seccion(nombre): 
                flash(f'Sección "{nombre}" creada con éxito!', 'success')
            else:
                flash(f'Error al crear la sección "{nombre}". Puede que el nombre ya exista.', 'danger')
        except Exception as e:
            flash(f'Error al crear sección: {e}', 'danger')
    elif action == 'edit':
        if id_seccion_form is not None and nombre: 
            try:
                # ASUMO: Seccion.update_seccion (método estándar)
                if Seccion.update_seccion(id_seccion_form, nombre): 
                    flash(f'Sección "{nombre}" actualizada con éxito!', 'success')
                else:
                    flash(f'Error al actualizar la sección "{nombre}". Verifique los datos o si el ID existe.', 'danger')
            except Exception as e:
                flash(f'Error al actualizar sección: {e}', 'danger')
        else:
            flash('Datos incompletos para actualizar sección.', 'danger')
    elif action == 'delete': 
        try:
            # ASUMO: Seccion.delete_seccion (método estándar)
            if Seccion.delete_seccion(id_seccion_form): 
                flash(f'Sección con ID {id_seccion_form} eliminada con éxito.', 'success')
            else:
                flash(f'No se pudo eliminar la sección con ID {id_seccion_form}.', 'danger')
        except Exception as e:
            flash(f'Error al eliminar sección: {e}', 'danger')
    else:
        flash('Acción no reconocida para secciones.', 'danger')
    
    return redirect(url_for('admin_bp.admin_dashboard', tab='secciones'))

@admin_bp.route('/admin/secciones/eliminar/<int:id>')
@admin_required
def eliminar_seccion(id): # Deja el parámetro 'id' porque así está en la ruta
    try:
        # ASUMO: Seccion.delete_seccion
        if Seccion.delete_seccion(id): 
            flash(f'Sección con ID {id} eliminada con éxito.', 'success')
        else:
            flash(f'No se pudo eliminar la sección con ID {id}.', 'danger')
    except Exception as e:
        flash(f'Error al eliminar sección: {e}', 'danger')
    return redirect(url_for('admin_bp.admin_dashboard', tab='secciones'))