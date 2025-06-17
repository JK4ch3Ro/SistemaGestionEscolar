from app.models.db import DB

class Matricula:
    def __init__(self, id_matricula, id_estudiante, id_curso, fecha_matricula):
        self.id_matricula = id_matricula
        self.id_estudiante = id_estudiante
        self.id_curso = id_curso
        self.fecha_matricula = fecha_matricula

    def to_dict(self):
        return {
            'id_matricula': self.id_matricula,
            'id_estudiante': self.id_estudiante,
            'id_curso': self.id_curso,
            'fecha_matricula': str(self.fecha_matricula) # Convertir a string para JSON/plantillas
        }

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Asegúrate de que los nombres de las columnas coincidan con tu DB
            cursor.execute("SELECT id_matricula, id_estudiante, id_curso, fecha_matricula FROM Matriculas")
            rows = cursor.fetchall()
            matriculas = []
            for row in rows:
                matriculas.append(Matricula(
                    row.id_matricula, # O row[0] si es tupla
                    row.id_estudiante, # O row[1]
                    row.id_curso, # O row[2]
                    row.fecha_matricula # O row[3]
                ))
            return matriculas
        except Exception as e:
            print(f"Error al obtener todas las matrículas: {e}")
            return []
        finally:
            DB.close_connection(conn)

    @staticmethod
    def crear_matricula(estudiante_username, curso_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Verifica si la matrícula ya existe para evitar duplicados
            cursor.execute("SELECT estudiante_username FROM Matriculas WHERE estudiante_username = ? AND curso_id = ?",
                           (estudiante_username, curso_id))
            if cursor.fetchone():
                return False # Ya matriculado

            cursor.execute("INSERT INTO Matriculas (estudiante_username, curso_id, fecha_matricula) VALUES (?, ?, GETDATE())",
                           (estudiante_username, curso_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            # print(f"Error al crear matrícula: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def eliminar_matricula(estudiante_username, curso_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Matriculas WHERE estudiante_username = ? AND curso_id = ?",
                           (estudiante_username, curso_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            # print(f"Error al eliminar matrícula: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def get_cursos_by_estudiante(estudiante_username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estudiante_username, curso_id, fecha_matricula FROM Matriculas WHERE estudiante_username = ?",
                       (estudiante_username,))
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Matricula(row.estudiante_username, row.curso_id, row.fecha_matricula) for row in rows]

    @staticmethod
    def get_estudiantes_by_curso(curso_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estudiante_username, curso_id, fecha_matricula FROM Matriculas WHERE curso_id = ?",
                       (curso_id,))
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Matricula(row.estudiante_username, row.curso_id, row.fecha_matricula) for row in rows]

    def to_dict(self):
        return {
            'estudiante_username': self.estudiante_username,
            'curso_id': self.curso_id,
            'fecha_matricula': self.fecha_matricula.isoformat() if self.fecha_matricula else None
        }