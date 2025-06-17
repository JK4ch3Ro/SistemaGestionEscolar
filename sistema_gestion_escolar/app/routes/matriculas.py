from flask import Blueprint, render_template
from app.models.matricula import Matricula
from app.utils.decorators import rol_required

matriculas_bp = Blueprint('matriculas', __name__)

@matriculas_bp.route('/matriculas')
@rol_required('admin') # Only admin can see the full list of enrollments
def listar_matriculas():
    matriculas = Matricula.obtener_todas_con_detalles()
    return render_template('matriculas/listar.html', matriculas=matriculas)

# No need for separate crear/eliminar routes here, as they are consolidated in admin.py