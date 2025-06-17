from app.models.db import DB

class Nota:
    def __init__(self, estudiante_username, curso_id, bimestre, valor):
        self.estudiante_username = estudiante_username
        self.curso_id = curso_id
        self.bimestre = bimestre
        self.valor = valor

    @staticmethod
    def guardar_o_actualizar_nota(estudiante_username, curso_id, bimestre, valor):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # SQL Server requiere un enfoque diferente para UPSERT.
            # Intenta actualizar; si no se actualiza ninguna fila, entonces inserta.
            cursor.execute("""
                UPDATE Notas
                SET valor = ?
                WHERE estudiante_username = ? AND curso_id = ? AND bimestre = ?
            """, (valor, estudiante_username, curso_id, bimestre))

            if cursor.rowcount == 0: # Si no se actualizó ninguna fila, significa que no existe, entonces inserta
                cursor.execute("""
                    INSERT INTO Notas (estudiante_username, curso_id, bimestre, valor)
                    VALUES (?, ?, ?, ?)
                """, (estudiante_username, curso_id, bimestre, valor))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            # print(f"Error al guardar/actualizar nota: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_notas_por_estudiante_y_curso(estudiante_username, curso_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estudiante_username, curso_id, bimestre, valor FROM Notas WHERE estudiante_username = ? AND curso_id = ?",
                       (estudiante_username, curso_id))
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Nota(row.estudiante_username, row.curso_id, row.bimestre, row.valor) for row in rows]

    @staticmethod
    def obtener_todas_las_notas():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT estudiante_username, curso_id, bimestre, valor FROM Notas")
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Nota(row.estudiante_username, row.curso_id, row.bimestre, row.valor) for row in rows]

    def to_dict(self):
        return {
            'estudiante_username': self.estudiante_username,
            'curso_id': self.curso_id,
            'bimestre': self.bimestre,
            'valor': self.valor
        }