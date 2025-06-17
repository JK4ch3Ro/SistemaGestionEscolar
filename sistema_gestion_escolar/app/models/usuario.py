# app/models/usuario.py

# Ya no necesitamos importar sqlite3 aquí directamente si DB maneja las conexiones
# from app.models.db import DB
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin

import pyodbc # Generalmente usas pyodbc para SQL Server
from app.models.db import DB # Tu módulo de conexión a DB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# La clase Usuario debe heredar de UserMixin
class Usuario(UserMixin):
    def __init__(self, username, password_hash, rol):
        self.username = username
        self.password_hash = password_hash
        self.rol = rol

    # Este método es requerido por Flask-Login para obtener el ID único del usuario
    def get_id(self):
        return self.username # Retorna el username como el ID único del usuario

    @staticmethod
    def crear(username, password, rol):
        conn = DB.get_connection()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        try:
            # En SQL Server, se usa INSERT INTO con VALUES, y generalmente se omiten los ';'
            cursor.execute("INSERT INTO Usuarios (username, password_hash, rol) VALUES (?, ?, ?)",
                           username, hashed_password, rol) # pyodbc usa argumentos directamente, no una tupla
            conn.commit()
            return Usuario(username, hashed_password, rol)
        except pyodbc.IntegrityError as e: # Cambiado de sqlite3.IntegrityError a pyodbc.IntegrityError
            conn.rollback()
            raise Exception(f"El usuario {username} ya existe o hay un error de integridad: {e}")
        finally:
            DB.close_connection(conn)

    @staticmethod
    def verificar_credenciales(username, password):
        conn = DB.get_connection()
        cursor = conn.cursor()
        # En SQL Server, las consultas son las mismas
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios WHERE username = ?", username)
        row = cursor.fetchone()
        DB.close_connection(conn)
        
        # Asumiendo que tu cursor devuelve un objeto de fila que permite acceso por nombre
        # Si no, deberías usar row[index] (ej. row[1] para password_hash)
        if row and check_password_hash(row.password_hash, password): # Acceso por atributo para pyodbc.Row
            return Usuario(row.username, row.password_hash, row.rol)
        return None

    @staticmethod
    def find_by_username(username): # Renombrado, como habíamos acordado
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios WHERE username = ?", username)
        row = cursor.fetchone()
        DB.close_connection(conn)
        if row:
            return Usuario(row.username, row.password_hash, row.rol)
        return None
    @staticmethod
    def obtener_por_username(username): # Renombrado, como habíamos acordado
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios WHERE username = ?", username)
        row = cursor.fetchone()
        DB.close_connection(conn)
        if row:
            return Usuario(row.username, row.password_hash, row.rol)
        return None

    @staticmethod
    def obtener_por_correo(correo):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT U.username, U.rol
            FROM Usuarios U
            LEFT JOIN Docentes D ON U.username = D.username
            LEFT JOIN Estudiantes E ON U.username = E.username
            WHERE D.correo = ? OR E.correo = ?
        """, correo, correo) # pyodbc argumentos directos
        row = cursor.fetchone()
        DB.close_connection(conn)
        return row is not None

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios")
        rows = cursor.fetchall()
        DB.close_connection(conn)
        # Asumiendo que row es un objeto que permite acceso por atributo
        return [Usuario(row.username, row.password_hash, row.rol) for row in rows]

    @staticmethod
    def actualizar(original_username, new_username, new_rol, new_password=None):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            if original_username != new_username:
                cursor.execute("UPDATE Usuarios SET username = ?, rol = ? WHERE username = ?",
                               new_username, new_rol, original_username)
            else:
                cursor.execute("UPDATE Usuarios SET rol = ? WHERE username = ?",
                               new_rol, new_username)

            if new_password:
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE Usuarios SET password_hash = ? WHERE username = ?",
                               hashed_password, new_username)
            
            conn.commit()
            return True
        except pyodbc.Error as e: # Captura errores generales de pyodbc
            conn.rollback()
            raise e
        finally:
            DB.close_connection(conn)

    @staticmethod
    def actualizar_username(original_username, new_username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Usuarios SET username = ? WHERE username = ?",
                           new_username, original_username)
            conn.commit()
            return True
        except pyodbc.Error as e:
            conn.rollback()
            raise e
        finally:
            DB.close_connection(conn)

    @staticmethod
    def delete_user(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Eliminar perfiles asociados primero (Docente, Estudiante).
            cursor.execute("DELETE FROM Docentes WHERE username = ?", username)
            cursor.execute("DELETE FROM Estudiantes WHERE username = ?", username)
            
            # Ahora eliminar el usuario
            cursor.execute("DELETE FROM Usuarios WHERE username = ?", username)
            conn.commit()
            return True
        except pyodbc.Error as e:
            conn.rollback()
            raise e
        finally:
            DB.close_connection(conn)

    def to_dict(self):
        return {
            'username': self.username,
            'rol': self.rol
        }
    @staticmethod
    def eliminar(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Eliminar perfiles asociados primero (Docente, Estudiante).
            cursor.execute("DELETE FROM Docentes WHERE username = ?", username)
            cursor.execute("DELETE FROM Estudiantes WHERE username = ?", username)
            
            # Ahora eliminar el usuario
            cursor.execute("DELETE FROM Usuarios WHERE username = ?", username)
            conn.commit()
            return True
        except pyodbc.Error as e:
            conn.rollback()
            raise e
        finally:
            DB.close_connection(conn)

    def to_dict(self):
        return {
            'username': self.username,
            'rol': self.rol
        }
    
    @staticmethod
    def get_users_without_docente_profile():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.rol
            FROM Usuarios u
            LEFT JOIN Docentes d ON u.username = d.username
            WHERE u.rol = 'docente' AND d.username IS NULL
        """)
        rows = cursor.fetchall()
        DB.close_connection(conn)
        # Asumiendo que row es un objeto que permite acceso por atributo
        return [Usuario(row.username, None, row.rol) for row in rows]

    @staticmethod
    def get_users_without_estudiante_profile():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.rol
            FROM Usuarios u
            LEFT JOIN Estudiantes e ON u.username = e.username
            WHERE u.rol = 'estudiante' AND e.username IS NULL
        """)
        rows = cursor.fetchall()
        DB.close_connection(conn)
        # Asumiendo que row es un objeto que permite acceso por atributo
        return [Usuario(row.username, None, row.rol) for row in rows]
    # app/models/usuario.py

# ... (resto del código) ...

    @staticmethod
    def verificar_credenciales(username, password):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios WHERE username = ?", username)
        row = cursor.fetchone()
        DB.close_connection(conn)
        
        # AJUSTE POTENCIAL AQUÍ:
        # Si row.password_hash, row.username, row.rol dan AttributeError (tuple object has no attribute)
        # Cámbialo a:
        # if row and check_password_hash(row[1], password): # row[1] para password_hash
        #     return Usuario(row[0], row[1], row[2]) # row[0] para username, row[2] para rol
        
        # Mantén la versión con atributos primero, es más legible si funciona
        if row and check_password_hash(row.password_hash, password):
            return Usuario(row.username, row.password_hash, row.rol)
        return None

    @staticmethod
    def find_by_username(username):
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios WHERE username = ?", username)
        row = cursor.fetchone()
        DB.close_connection(conn)
        if row:
            # AJUSTE POTENCIAL AQUÍ:
            # Si row.username, row.password_hash, row.rol dan AttributeError
            # Cámbialo a:
            # return Usuario(row[0], row[1], row[2])
            return Usuario(row.username, row.password_hash, row.rol)
        return None

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash, rol FROM Usuarios")
        rows = cursor.fetchall()
        DB.close_connection(conn)
        # AJUSTE POTENCIAL AQUÍ:
        # Si row.username, row.password_hash, row.rol dan AttributeError
        # Cámbialo a:
        # return [Usuario(r[0], r[1], r[2]) for r in rows]
        return [Usuario(row.username, row.password_hash, row.rol) for row in rows]

    # ... Y de manera similar para get_users_without_docente_profile y get_users_without_estudiante_profile
    @staticmethod
    def get_users_without_docente_profile():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.rol
            FROM Usuarios u
            LEFT JOIN Docentes d ON u.username = d.username
            WHERE u.rol = 'docente' AND d.username IS NULL
        """)
        rows = cursor.fetchall()
        DB.close_connection(conn)
        # AJUSTE POTENCIAL AQUÍ:
        # return [Usuario(row[0], None, row[1]) for row in rows]
        return [Usuario(row.username, None, row.rol) for row in rows]

    @staticmethod
    def get_users_without_estudiante_profile():
        conn = DB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.username, u.rol
            FROM Usuarios u
            LEFT JOIN Estudiantes e ON u.username = e.username
            WHERE u.rol = 'estudiante' AND e.username IS NULL
        """)
        rows = cursor.fetchall()
        DB.close_connection(conn)
        # AJUSTE POTENCIAL AQUÍ:
        # return [Usuario(row[0], None, row[1]) for row in rows]
        return [Usuario(row.username, None, row.rol) for row in rows]

# ... (resto del código) ...