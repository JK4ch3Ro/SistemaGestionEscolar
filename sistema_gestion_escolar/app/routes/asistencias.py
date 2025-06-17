from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models.asistencia import Asistencia
from app.models.estudiante import Estudiante
from app.utils.decorators import rol_required

asistencias_bp = Blueprint('asistencias', __name__)

@asistencias_bp.route('/mis_asistencias')
@rol_required('estudiante')
def ver_mis_asistencias():
    estudiante_username = session.get('usuario')
    estudiante = Estudiante.obtener_por_username(estudiante_username)
    if not estudiante:
        flash('Datos de estudiante no encontrados.', 'danger')
        return redirect(url_for('auth.logout'))

    # This route might become obsolete as attendance will be displayed in alumno.inicio
    # For now, it could show a summary or detailed list for all courses.

    # Get all courses student is enrolled in
    from app.models.matricula import Matricula
    matriculas = Matricula.obtener_matriculas_por_estudiante_con_detalles(estudiante_username)
    
    cursos_con_asistencia = []
    for matricula in matriculas:
        curso_data = matricula.curso.to_dict()
        # Get a detailed list of attendance for this student in this course
        detalles_asistencia = Asistencia.obtener_asistencia_detallada_por_estudiante_y_curso(estudiante_username, matricula.curso_id) # You'll need this method
        resumen_asistencia = Asistencia.obtener_resumen_asistencia_por_estudiante_y_curso(estudiante_username, matricula.curso_id) # You'll need this method

        curso_data['asistencia_detalles'] = detalles_asistencia
        curso_data['asistencia_resumen'] = resumen_asistencia
        cursos_con_asistencia.append(curso_data)

    return render_template('asistencias/ver_asistencias_alumno.html', 
                           estudiante=estudiante, 
                           cursos_con_asistencia=cursos_con_asistencia)