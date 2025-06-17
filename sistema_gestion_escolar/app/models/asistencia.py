from app.models.db import DB
from datetime import date # Asegúrate de que date esté importado

class Asistencia:
    def __init__(self, estudiante_username, curso_id, fecha, presente):
        self.estudiante_username = estudiante_username
        self.curso_id = curso_id
        self.fecha = fecha
        self.presente = presente

    @staticmethod
    def guardar_o_actualizar_asistencia(estudiante_username, curso_id, fecha, presente):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # SQL Server: Intenta actualizar; si no se actualiza ninguna fila, entonces inserta.
            cursor.execute("""
                UPDATE Asistencias
                SET presente = ?
                WHERE estudiante_username = ? AND curso_id = ? AND fecha = ?
            """, (presente, estudiante_username, curso_id, fecha))

            if cursor.rowcount == 0: # Si no se actualizó ninguna fila, inserta
                cursor.execute("""
                    INSERT INTO Asistencias (estudiante_username, curso_id, fecha, presente)
                    VALUES (?, ?, ?, ?)
                """, (estudiante_username, curso_id, fecha, presente))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            # print(f"Error al guardar/actualizar asistencia: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_asistencia_por_estudiante_curso_fecha(estudiante_username, curso_id, fecha):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estudiante_username, curso_id, fecha, presente FROM Asistencias WHERE estudiante_username = ? AND curso_id = ? AND fecha = ?",
                       (estudiante_username, curso_id, fecha))
        row = cursor.fetchone()
        DB.close_connection(conn)
        if row:
            return Asistencia(row.estudiante_username, row.curso_id, row.fecha, row.presente)
        return None

    @staticmethod
    def obtener_asistencias_por_estudiante_y_curso(estudiante_username, curso_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estudiante_username, curso_id, fecha, presente FROM Asistencias WHERE estudiante_username = ? AND curso_id = ? ORDER BY fecha DESC",
                       (estudiante_username, curso_id))
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Asistencia(row.estudiante_username, row.curso_id, row.fecha, row.presente) for row in rows]

    def to_dict(self):
        return {
            'estudiante_username': self.estudiante_username,
            'curso_id': self.curso_id,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'presente': self.presente
        }