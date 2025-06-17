# app/models/seccion.py

import pyodbc # Import pyodbc for handling specific database errors
from app.models.db import DB # Your database connection utility

class Seccion:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    @staticmethod
    def crear_seccion(nombre):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Secciones (nombre) VALUES (?)", (nombre,))
            # For SQL Server, use SCOPE_IDENTITY() to get the last inserted ID
            cursor.execute("SELECT SCOPE_IDENTITY();")
            new_id = cursor.fetchone()[0] # Get the value from the single-element tuple
            conn.commit()
            return Seccion(int(new_id), nombre) # Convert ID to int for consistency
        except pyodbc.IntegrityError as e:
            conn.rollback()
            # Check for unique constraint violation (case-insensitive)
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise Exception(f"Error: La sección '{nombre}' ya existe.")
            else:
                raise Exception(f"Error de integridad al crear sección: {e}")
        except Exception as e:
            conn.rollback()
            print(f"Error al crear sección: {e}") # Log the specific error
            raise Exception(f"Error desconocido al crear la sección: {e}")
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_por_id(id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, nombre FROM Secciones WHERE id = ?", (id,))
            row = cursor.fetchone()
            if row:
                # Access by index (row[0] for id, row[1] for nombre)
                return Seccion(row[0], row[1])
            return None
        except Exception as e:
            print(f"Error al obtener sección por ID: {e}")
            return None
        finally:
            DB.close_connection(conn)

    @staticmethod
    def obtener_todos():
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, nombre FROM Secciones")
            rows = cursor.fetchall()
            # Iterate and access by index (row[0] for id, row[1] for nombre)
            return [Seccion(row[0], row[1]) for row in rows]
        except Exception as e:
            print(f"Error al obtener todas las secciones: {e}")
            return []
        finally:
            DB.close_connection(conn)

    @staticmethod
    def update_seccion(id, nombre):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Secciones SET nombre = ? WHERE id = ?", (nombre, id))
            conn.commit()
            return cursor.rowcount > 0 # Returns True if at least one row was updated
        except pyodbc.IntegrityError as e:
            conn.rollback()
            if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                raise Exception(f"Error: El nombre de sección '{nombre}' ya está en uso.")
            else:
                raise Exception(f"Error de integridad al actualizar sección: {e}")
        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar sección: {e}") # Log the specific error
            raise Exception(f"Error desconocido al actualizar la sección: {e}")
        finally:
            DB.close_connection(conn)

    @staticmethod
    def delete_seccion(id):
        conn = DB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Secciones WHERE id = ?", (id,))
            conn.commit()
            return cursor.rowcount > 0 # Returns True if at least one row was deleted
        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar sección: {e}") # Log the specific error
            # Check for foreign key constraint violation
            if "foreign key constraint" in str(e).lower():
                raise Exception(f"No se puede eliminar la sección {id} porque tiene dependencias (ej. estudiantes) asociadas.")
            else:
                raise # Re-raise other unexpected exceptions
        finally:
            DB.close_connection(conn)

    # Useful method for converting the object to a dictionary (e.g., for APIs or templates)
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre
        }