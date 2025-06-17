from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.models.nota import Nota
from app.models.estudiante import Estudiante
from app.utils.decorators import rol_required

notas_bp = Blueprint('notas', __name__)

@notas_bp.route('/mis_notas')
@rol_required('estudiante')
def ver_mis_notas():
    estudiante_username = session.get('usuario')
    estudiante = Estudiante.obtener_por_username(estudiante_username)
    if not estudiante:
        flash('Datos de estudiante no encontrados.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # This route might become obsolete as notes will be displayed in alumno.inicio
    # For now, it could show all notes for all courses.
    
    # Get all courses student is enrolled in
    from app.models.matricula import Matricula
    matriculas = Matricula.obtener_matriculas_por_estudiante_con_detalles(estudiante_username)
    
    cursos_con_notas = []
    for matricula in matriculas:
        curso_data = matricula.curso.to_dict()
        notas_bimestrales = Nota.obtener_notas_por_estudiante_y_curso(estudiante_username, matricula.curso_id)
        curso_data['notas'] = {nota.bimestre: nota.valor for nota in notas_bimestrales} if notas_bimestrales else {}
        cursos_con_notas.append(curso_data)

    return render_template('notas/ver_notas_alumno.html', 
                           estudiante=estudiante, 
                           cursos_con_notas=cursos_con_notas)