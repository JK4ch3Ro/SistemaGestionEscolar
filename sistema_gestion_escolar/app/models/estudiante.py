import pyodbc # Importar pyodbc para SQL Server
from app.models.db import DB
from app.models.usuario import Usuario

class Estudiante:
    def __init__(self, username, nombres, apellidos, dni, correo, grado_id, seccion_id):
        # Alineamos los atributos del modelo con las columnas EXACTAS de la tabla Estudiantes
        self.username = username
        self.nombres = nombres
        self.apellidos = apellidos
        self.dni = dni
        self.correo = correo
        self.grado_id = grado_id # Ahora coincide con la DB: 'grado_id'
        self.seccion_id = seccion_id # Ahora coincide con la DB: 'seccion_id'

        # Eliminamos fecha_nacimiento y genero porque no existen en tu tabla Estudiantes
        # Si estas columnas son necesarias, DEBES añadirlas a tu CREATE TABLE Estudiantes

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Selecciona las columnas en el mismo orden que el __init__
            cursor.execute("SELECT username, nombres, apellidos, dni, correo, grado_id, seccion_id FROM Estudiantes")
            rows = cursor.fetchall()
            # Pasa las filas directamente al constructor, ya que el orden coincide
            estudiantes = [Estudiante(*row) for row in rows]
            return estudiantes
        except Exception as e:
            print(f"Error al obtener todos los estudiantes: {e}")
            return []
        finally:
            DB.close_connection(conn)

    @staticmethod
    def find_by_username(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Selecciona las columnas en el mismo orden que el __init__
            cursor.execute(
                "SELECT username, nombres, apellidos, dni, correo, grado_id, seccion_id FROM Estudiantes WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                # Pasa la fila directamente al constructor
                return Estudiante(*row)
            return None
        except Exception as e:
            print(f"Error al buscar estudiante por username: {e}")
            return None
        finally:
            DB.close_connection(conn)

    def to_dict(self):
        # Aseguramos que los nombres de los atributos coincidan con los del __init__
        return {
            'username': self.username,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'dni': self.dni,
            'correo': self.correo,
            'grado_id': self.grado_id,
            'seccion_id': self.seccion_id
        }

    @staticmethod
    def crear_estudiante(username, nombres, apellidos, dni, correo, grado_id, seccion_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # La sentencia INSERT ya estaba correcta según tu CREATE TABLE
            # Los parámetros grado_id y seccion_id deben venir con un valor (no None)
            cursor.execute("INSERT INTO Estudiantes (username, nombres, apellidos, dni, correo, grado_id, seccion_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (username, nombres, apellidos, dni, correo, grado_id, seccion_id))
            conn.commit()
            return True
        except pyodbc.IntegrityError as e:
            conn.rollback()
            # El error 23000 es la violación de integridad (ej. NOT NULL, UNIQUE, FK)
            # Imprime el error específico para depuración
            print(f"Error de integridad al crear estudiante: {e}")
            return False
        except Exception as e:
            conn.rollback()
            print(f"Error general al crear estudiante: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_todos_con_grado_seccion():
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT E.username, E.nombres, E.apellidos, E.dni, E.correo,
                       G.nombre AS grado_nombre, S.nombre AS seccion_nombre, U.rol
                FROM Estudiantes E
                JOIN Grados G ON E.grado_id = G.id 
                JOIN Secciones S ON E.seccion_id = S.id 
                JOIN Usuarios U ON E.username = U.username
            """)
            column_names = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(column_names):
                    row_dict[col_name] = row[i]
                result.append(row_dict)
            return result

        except Exception as e:
            print(f"Error al obtener todos los estudiantes con grado y sección: {e}")
            return []
        finally:
            DB.close_connection(conn)

    @staticmethod
    def update_estudiante(username, nombres, apellidos, dni, correo, grado_id, seccion_id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # La sentencia UPDATE ya estaba correcta según tu CREATE TABLE
            cursor.execute("UPDATE Estudiantes SET nombres = ?, apellidos = ?, dni = ?, correo = ?, grado_id = ?, seccion_id = ? WHERE username = ?",
                           (nombres, apellidos, dni, correo, grado_id, seccion_id, username))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar estudiante: {e}")
            return False
        finally:
            DB.close_connection(conn)

    @staticmethod
    def delete_estudiante(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Elimina registros en tablas que referencian al estudiante usando 'estudiante_username'
            # CORREGIDO: Cambiado 'username' a 'estudiante_username' en estas líneas
            cursor.execute("DELETE FROM Matriculas WHERE estudiante_username = ?", (username,))
            # Si tienes tablas Notas o Asistencias, asegúrate de que también usen 'estudiante_username'
            # Si no las usas, puedes eliminar estas líneas.
            cursor.execute("DELETE FROM Notas WHERE estudiante_username = ?", (username,))
            cursor.execute("DELETE FROM Asistencias WHERE estudiante_username = ?", (username,))

            # Luego, elimina el perfil de estudiante.
            # Esta línea ELIMINA el registro de la tabla Estudiantes.
            # Si tu Foreign Key de Estudiantes a Usuarios es ON DELETE CASCADE,
            # y si las tablas Notas/Matriculas/Asistencias también tienen ON DELETE CASCADE a Estudiantes,
            # entonces SOLO necesitarías llamar a Usuario.eliminar(username) y todo lo demás se borraría automáticamente.
            # Sin embargo, si no tienes esas cascadas configuradas en tu DB, estas DELETEs explícitas son necesarias.
            cursor.execute("DELETE FROM Estudiantes WHERE username = ?", (username,))
            
            # Finalmente, elimina el usuario asociado.
            # Esto es lo que debería disparar el borrado en cascada si tienes esa configuración.
            Usuario.eliminar(username) 
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar estudiante: {e}")
            return False
        finally:
            DB.close_connection(conn)