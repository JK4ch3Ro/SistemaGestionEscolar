# app/models/grado.py

import pyodbc
from app.models.db import DB

class Grado:
    # Constructor: Los atributos del objeto ahora coinciden con los nombres de tus columnas de DB
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    @staticmethod
    def crear_grado(nombre):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # La columna es 'nombre', no 'nombre_grado'
            cursor.execute("INSERT INTO Grados (nombre) VALUES (?)", (nombre,))
            cursor.execute("SELECT SCOPE_IDENTITY();")
            new_id = cursor.fetchone()[0] # Obtiene el ID autoincremental
            conn.commit()
            return Grado(int(new_id), nombre) # Retorna el objeto Grado con el ID real
        except pyodbc.IntegrityError as e:
            conn.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise Exception(f"Error: El grado '{nombre}' ya existe.")
            else:
                raise Exception(f"Error de integridad al crear grado: {e}")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error desconocido al crear el grado: {e}")
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_por_id(id): # Ahora el parámetro es 'id'
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Las columnas son 'id' y 'nombre'
            cursor.execute("SELECT id, nombre FROM Grados WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                # Acceso por índice si el cursor devuelve tuplas
                return Grado(row[0], row[1])
            return None
        except Exception as e:
            print(f"Error al obtener grado por ID: {e}")
            return None
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # Las columnas son 'id' y 'nombre'
            cursor.execute("SELECT id, nombre FROM Grados")
            rows = cursor.fetchall()
            return [Grado(row[0], row[1]) for row in rows]
        except Exception as e:
            print(f"Error al obtener todos los grados: {e}")
            return []
        finally:
            DB.close_connection(conn)

    @staticmethod
    def update_grado(id, nombre): # Los parámetros son 'id' y 'nombre'
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            # La columna es 'nombre' y la condición es por 'id'
            cursor.execute("UPDATE Grados SET nombre = ? WHERE id = ?", (nombre, id))
            conn.commit()
            return cursor.rowcount > 0
        except pyodbc.IntegrityError as e:
            conn.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise Exception(f"Error: El nombre de grado '{nombre}' ya está en uso.")
            else:
                raise Exception(f"Error de integridad al actualizar grado: {e}")
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error desconocido al actualizar el grado: {e}")
        finally:
            DB.close_connection(conn)

    @staticmethod
    def delete_grado(id): # El parámetro es 'id'
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Grados WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            if "foreign key constraint" in str(e).lower():
                raise Exception(f"No se puede eliminar el grado {id} porque tiene estudiantes u otras dependencias asociadas.")
            else:
                raise
        finally:
            DB.close_connection(conn)

    # Método útil para convertir el objeto a un diccionario, si lo necesitas en algún momento.
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }