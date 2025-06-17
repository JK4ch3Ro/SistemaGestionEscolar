from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta # Importa timedelta para manejo de fechas

from app.models.docente import Docente
from app.models.curso import Curso
from app.models.estudiante import Estudiante
from app.models.nota import Nota
from app.models.asistencia import Asistencia
from app.models.matricula import Matricula
from app.models.grado import Grado 
from app.models.seccion import Seccion 

# Asegúrate de que este 'template_folder' sea correcto.
# Si tus templates están en 'app/templates/docente', y este es el blueprint de 'docente',
# entonces template_folder='../templates' es correcto si tu app.py usa Blueprint de la raíz.
# Si tu app.py registra el blueprint con un URL prefix, por ejemplo '/docente', entonces
# 'template_folder' podría ser relativo a 'app/templates'. Mantendremos '../templates' por ahora.
docente_bp = Blueprint('docente_bp', __name__, template_folder='../templates')

# Decorador para restringir el acceso solo a docentes
def docente_required(f):
    @login_required
    def wrap(*args, **kwargs):
        if not hasattr(current_user, 'rol') or current_user.rol != 'docente':
            flash('No tienes permiso para acceder a esta página.', 'danger')
            return redirect(url_for('dashboard_bp.dashboard')) # Asumo 'dashboard_bp.dashboard' es la ruta general
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__ # Asegura que el nombre de la función decorada sea único
    return wrap



@docente_bp.route('/docente/inicio')
@docente_required
def docente_dashboard():
    docente_username = current_user.username
    docente_info = Docente.find_by_username(docente_username)

    if not docente_info:
        flash('Perfil de docente no encontrado. Por favor, contacte al administrador.', 'danger')
        return redirect(url_for('dashboard_bp.dashboard'))

    cursos_del_docente = Curso.get_cursos_by_docente(docente_username)
    
    # ***OPTIMIZACIÓN IMPORTANTE***:
    # Ya no necesitas cargar estudiantes_por_curso, grados_map, secciones_map aquí,
    # porque la información detallada de los estudiantes y la gestión
    # se realizará en la nueva página 'gestion_curso_detalle.html'.
    # Si quisieras mostrar el número de estudiantes por curso en el dashboard,
    # tendrías que hacer una pequeña consulta para obtener solo el conteo.
    # Por simplicidad, el dashboard.html actualizado ya no los muestra si no los pasas.

    return render_template('docente/dashboard.html',
                           docente_info=docente_info,
                           cursos_del_docente=cursos_del_docente) # Solo pasamos la información básica



#  NUEVA RUTA PARA GESTIÓN DETALLADA DE UN CURSO 
@docente_bp.route('/docente/cursos/<int:curso_id>/gestion', methods=['GET']) # Solo GET, los POST van a rutas separadas
@docente_required
def gestion_curso_detalle(curso_id):
    docente_username = current_user.username
    curso = Curso.find_by_id(curso_id)

    # Verificar que el curso existe y pertenece al docente actual
    if not curso or curso.docente_username != docente_username:
        flash('Curso no encontrado o no autorizado para la gestión.', 'danger')
        return redirect(url_for('docente_bp.docente_dashboard'))

    # Obtener estudiantes matriculados para este curso
    estudiantes_matriculados_raw = Matricula.get_estudiantes_by_curso(curso.id)
    estudiantes_para_curso = []

    # Pre-cargar los nombres de grados y secciones para eficiencia
    grados_map = {g.id: g.nombre for g in Grado.obtener_todos()}
    secciones_map = {s.id: s.nombre for s in Seccion.obtener_todos()}

    # Definir las fechas para mostrar asistencia (ej: hoy, ayer, hace 2 días)
    fechas_asistencia_interes = [
        date.today(),
        date.today() - timedelta(days=1),
        date.today() - timedelta(days=2)
        # Puedes añadir más fechas o lógica para un rango de fechas si es necesario
    ]
    # Ordenar las fechas de la más reciente a la más antigua para la visualización en la tabla
    fechas_asistencia_interes.sort(reverse=True)


    for matricula_obj in estudiantes_matriculados_raw:
        estudiante_obj = Estudiante.find_by_username(matricula_obj.estudiante_username)
        
        if estudiante_obj:
            est_data_for_template = estudiante_obj.to_dict()
            
            est_data_for_template['grado_nombre'] = grados_map.get(estudiante_obj.grado_id, 'N/A')
            est_data_for_template['seccion_nombre'] = secciones_map.get(estudiante_obj.seccion_id, 'N/A')

            # Obtener notas del estudiante para este curso
            notas = Nota.obtener_notas_por_estudiante_y_curso(estudiante_obj.username, curso.id)
            est_data_for_template['notas'] = {n.bimestre: n.valor for n in notas}

            # Obtener asistencia para las fechas de interés
            asistencia_fechas = {}
            for f_asist in fechas_asistencia_interes:
                asistencia_record = Asistencia.obtener_asistencia_por_estudiante_curso_fecha(estudiante_obj.username, curso.id, f_asist)
                # Almacena el estado booleano (True/False) o None si no hay registro
                asistencia_fechas[f_asist.strftime('%Y-%m-%d')] = asistencia_record.presente if asistencia_record else None
            est_data_for_template['asistencia_fechas'] = asistencia_fechas

            estudiantes_para_curso.append(est_data_for_template)
    
    return render_template('docente/gestion_curso_detalle.html',
                           curso=curso,
                           estudiantes=estudiantes_para_curso,
                           fechas_asistencia=fechas_asistencia_interes # Pasamos las fechas para los encabezados de la tabla
                           )



@docente_bp.route('/docente/gestionar_nota', methods=['POST'])
@docente_required
def gestionar_nota():
    estudiante_username = request.form['estudiante_username']
    curso_id = request.form['curso_id']
    bimestre = request.form['bimestre']
    valor = request.form['valor']

    try:
        valor = float(valor)
        curso_id = int(curso_id)
        if not (0 <= valor <= 20): # Asumiendo notas de 0 a 20
            flash('La nota debe estar entre 0 y 20.', 'danger')
            # Redirige a la página de detalle del curso y al estudiante
            return redirect(url_for('docente_bp.gestion_curso_detalle', curso_id=curso_id, _anchor=f'estudiante-{estudiante_username}'))

        if Nota.guardar_o_actualizar_nota(estudiante_username, curso_id, bimestre, valor):
            flash(f'Nota de {estudiante_username} (Bim. {bimestre}) guardada con éxito!', 'success')
        else:
            flash('Error al guardar la nota. Asegúrese de que todos los datos sean válidos.', 'danger')
    except ValueError:
        flash('El valor de la nota es inválido. Por favor, ingrese un número.', 'danger')
    except Exception as e:
        flash(f'Error al procesar la nota: {e}', 'danger')

    # Redirige a la página de detalle del curso y al estudiante
    return redirect(url_for('docente_bp.gestion_curso_detalle', curso_id=curso_id, _anchor=f'estudiante-{estudiante_username}'))



@docente_bp.route('/docente/gestionar_asistencia', methods=['POST'])
@docente_required
def gestionar_asistencia():
    estudiante_username = request.form['estudiante_username']
    curso_id = request.form['curso_id']
    fecha_str = request.form.get('fecha') # Ahora la fecha siempre vendrá del hidden input
    presente_str = request.form.get('presente') # 'True' o 'False'

    try:
        curso_id = int(curso_id)
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        presente = presente_str == 'True'

        if Asistencia.guardar_o_actualizar_asistencia(estudiante_username, curso_id, fecha, presente):
            flash(f'Asistencia de {estudiante_username} para el {fecha_str} registrada con éxito!', 'success')
        else:
            flash('Error al registrar la asistencia. Asegúrese de que todos los datos sean válidos.', 'danger')
    except ValueError:
        flash('Formato de fecha o valor de presencia inválido.', 'danger')
    except Exception as e:
        flash(f'Error al procesar la asistencia: {e}', 'danger')

    # Redirige a la página de detalle del curso y al estudiante
    return redirect(url_for('docente_bp.gestion_curso_detalle', curso_id=curso_id, _anchor=f'estudiante-{estudiante_username}'))

#  Las rutas gestionar_notas_curso y gestionar_asistencia_curso ya no se usarán directamente 
# Puedes eliminarlas o mantenerlas si tienes otros casos de uso para ellas.
# En este nuevo esquema, la ruta `gestion_curso_detalle` centraliza la carga de datos.
# Si decides eliminarlas, asegúrate de que ningún otro enlace las apunte.