from app.models.db import DB
# from app.models.docente import Docente # ELIMINA o COMENTA esta línea

class Curso:
    def __init__(self, id, nombre, docente_username=None):
        self.id = id
        self.nombre = nombre
        self.docente_username = docente_username
        self._docente = None # Para almacenar el objeto Docente si se carga

    @property
    def docente(self):
        # Carga el objeto Docente solo si se necesita y aún no está cargado
        if self._docente is None and self.docente_username:
            from app.models.docente import Docente # Importar aquí para evitar circularidad
            self._docente = Docente.find_by_username(self.docente_username)
        return self._docente

    @staticmethod
    def crear_curso(nombre, docente_username=None):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Cursos (nombre, docente_username) VALUES (?, ?)",
                           (nombre, docente_username))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            # print(f"Error al crear curso: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def find_by_id(id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, docente_username FROM Cursos WHERE id = ?", (id,))
        row = cursor.fetchone()
        DB.close_connection(conn)
        if row:
            return Curso(row.id, row.nombre, row.docente_username)
        return None

    @staticmethod
    def update_curso(id, nombre, docente_username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Cursos SET nombre = ?, docente_username = ? WHERE id = ?",
                           (nombre, docente_username, id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            # print(f"Error al actualizar curso: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def delete_curso(id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # También podrías querer manejar qué pasa con las notas/asistencias de este curso
            # Por ahora, las FK con CASCADE DELETE en SQL Server manejarán esto si están bien configuradas.
            cursor.execute("DELETE FROM Cursos WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            # print(f"Error al eliminar curso: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, docente_username FROM Cursos")
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Curso(row.id, row.nombre, row.docente_username) for row in rows]

    @staticmethod
    def get_cursos_by_docente(docente_username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, docente_username FROM Cursos WHERE docente_username = ?", (docente_username,))
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Curso(row.id, row.nombre, row.docente_username) for row in rows]

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'docente_username': self.docente_username
        }