# app/models/db.py

import pyodbc
from flask import current_app # Para acceder a la configuración de la app

class DB:
    _connection_string = None

    @staticmethod
    def init(app_config):
        # La cadena de conexión a SQL Server se obtiene de la configuración de Flask
        DB._connection_string = app_config.get('SQLALCHEMY_DATABASE_URI_SQLSERVER') 
        if not DB._connection_string:
            raise ValueError("SQLALCHEMY_DATABASE_URI_SQLSERVER no está configurado en tu app config.")

    @staticmethod
    def get_connection():
        """
        Abre y retorna una nueva conexión a la base de datos SQL Server.
        """
        if not DB._connection_string:
            # Si se llama get_connection antes de init, podemos intentar obtenerlo de current_app
            if current_app:
                DB._connection_string = current_app.config.get('SQLALCHEMY_DATABASE_URI_SQLSERVER')
            if not DB._connection_string:
                raise Exception("Cadena de conexión a SQL Server no inicializada. Llama DB.init(app.config) o configura SQLALCHEMY_DATABASE_URI_SQLSERVER.")
                
        try:
            conn = pyodbc.connect(DB._connection_string)
            # ¡LÍNEA ELIMINADA!
            # conn.set_attr(pyodbc.SQL_ATTR_CURSOR_LOCATION, pyodbc.SQL_CUR_USE_FOR_GET_BOOKMARK) 
            return conn
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            # Puedes añadir más manejo de errores específicos aquí si lo necesitas
            if sqlstate == '28000': 
                raise Exception("Error de autenticación al conectar a SQL Server. Verifica tu usuario y contraseña.")
            else:
                raise Exception(f"Error al conectar a SQL Server: {ex}")

    @staticmethod
    def close_connection(conn):
        """
        Cierra la conexión a la base de datos SQL Server.
        """
        if conn:
            conn.close()

    @staticmethod
    def commit_and_close(conn):
        """
        Realiza un commit en la conexión y luego la cierra.
        """
        if conn:
            conn.commit()
            conn.close()