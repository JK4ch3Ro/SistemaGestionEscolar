import os

class Config:
    SECRET_KEY = 'clave-secreta' # O una clave más segura como os.environ.get('SECRET_KEY')

    # Configuración de SQL Server
    # Ensamblamos la cadena de conexión completa para pyodbc
    SQLALCHEMY_DATABASE_URI_SQLSERVER = (
        "DRIVER={ODBC Driver 17 for SQL Server};"  # ¡Asegúrate de que este driver esté instalado!
        f"SERVER={os.environ.get('SQL_SERVER', 'localhost')};" # Usa localhost o el nombre de tu instancia (ej. .\SQLEXPRESS)
        f"DATABASE={os.environ.get('SQL_DATABASE', 'sistema_gestion_escolar')};"
        f"UID={os.environ.get('SQL_USERNAME', 'sa')};"
        f"PWD={os.environ.get('SQL_PASSWORD', 'daniel1908@Peru')};"
    )

    # Puedes mantener esto si aún lo usas para algo, pero la app.init() ya no lo usará
    # DATABASE = 'database.db' # Esta era para SQLite