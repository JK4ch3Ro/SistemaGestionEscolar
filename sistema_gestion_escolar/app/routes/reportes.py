from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models.matricula import Matricula
from app.models.grado import Grado
from app.utils.decorators import rol_required

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes')
@rol_required('admin')
def inicio_reportes():
    return render_template('reportes/dashboard.html')

@reportes_bp.route('/reportes/matriculas_por_grado')
@rol_required('admin')
def reporte_matriculas_por_grado():
    # This method needs to be implemented in Matricula model to get counts
    reporte_data = Matricula.contar_matriculas_por_grado() 
    
    # You might want to get degree names instead of IDs
    grados = {g.id: g.nombre for g in Grado.obtener_todos()}
    
    reporte_final = {grados.get(gid, f'Grado ID {gid}'): count for gid, count in reporte_data.items()}

    return render_template('reportes/matriculas_grado.html', reporte_data=reporte_final)

# Add more report routes as needed