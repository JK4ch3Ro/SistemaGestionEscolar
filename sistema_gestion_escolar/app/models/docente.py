from app.models.db import DB
# from app.models.curso import Curso  # ELIMINA o COMENTA esta línea

class Docente:
    def __init__(self, username, nombres, apellidos, dni, correo):
        self.username = username
        self.nombres = nombres
        self.apellidos = apellidos
        self.dni = dni
        self.correo = correo

    @staticmethod
    def crear_docente(username, nombres, apellidos, dni, correo):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Primero verifica si el usuario con ese username ya tiene un perfil de docente
            cursor.execute("SELECT username FROM Docentes WHERE username = ?", (username,))
            if cursor.fetchone():
                return False # Ya existe un perfil de docente para este usuario

            cursor.execute("INSERT INTO Docentes (username, nombres, apellidos, dni, correo) VALUES (?, ?, ?, ?, ?)",
                           (username, nombres, apellidos, dni, correo))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            # Puedes loggear el error aquí: print(f"Error al crear docente: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def find_by_username(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, nombres, apellidos, dni, correo FROM Docentes WHERE username = ?", (username,))
        row = cursor.fetchone()
        DB.close_connection(conn)
        if row:
            return Docente(row.username, row.nombres, row.apellidos, row.dni, row.correo)
        return None

    @staticmethod
    def update_docente(username, nombres, apellidos, dni, correo):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Docentes SET nombres = ?, apellidos = ?, dni = ?, correo = ? WHERE username = ?",
                           (nombres, apellidos, dni, correo, username))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            # print(f"Error al actualizar docente: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def delete_docente(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Considerar qué hacer con los cursos asignados a este docente
            # Opción 1: Desvincular cursos (establecer docente_username a NULL)
            cursor.execute("UPDATE Cursos SET docente_username = NULL WHERE docente_username = ?", (username,))
            
            cursor.execute("DELETE FROM Docentes WHERE username = ?", (username,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            # print(f"Error al eliminar docente: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, nombres, apellidos, dni, correo FROM Docentes")
        rows = cursor.fetchall()
        DB.close_connection(conn)
        return [Docente(row.username, row.nombres, row.apellidos, row.dni, row.correo) for row in rows]

    @staticmethod
    def get_docentes_con_cursos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        # Importar Curso aquí para evitar la importación circular a nivel global
        from app.models.curso import Curso 
        
        cursor.execute("""
            SELECT d.username, d.nombres, d.apellidos, d.dni, d.correo,
                   c.id AS curso_id, c.nombre AS curso_nombre
            FROM Docentes d
            LEFT JOIN Cursos c ON d.username = c.docente_username
            ORDER BY d.apellidos, d.nombres, c.nombre
        """)
        rows = cursor.fetchall()
        DB.close_connection(conn)

        docentes_map = {}
        for row in rows:
            username = row.username
            if username not in docentes_map:
                docente = Docente(row.username, row.nombres, row.apellidos, row.dni, row.correo)
                docente.cursos_impartidos = []
                docentes_map[username] = docente
            
            if row.curso_id:
                docentes_map[username].cursos_impartidos.append(Curso(row.curso_id, row.curso_nombre, username))
        
        return list(docentes_map.values())

    def to_dict(self):
        return {
            'username': self.username,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'dni': self.dni,
            'correo': self.correo
        }