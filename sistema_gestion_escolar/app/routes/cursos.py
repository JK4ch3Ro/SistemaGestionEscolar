from flask import Blueprint, render_template
from app.models.curso import Curso
from app.utils.decorators import rol_required

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/cursos')
@rol_required('admin') # Only admin can see the full list of courses
def listar_cursos():
    cursos = Curso.obtener_todos_con_docente_info()
    return render_template('cursos/listar.html', cursos=cursos)

# No need for separate crear/editar/eliminar routes here, as they are consolidated in admin.py