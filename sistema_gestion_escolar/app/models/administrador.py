from app.models.db import DB
from app.models.usuario import Usuario

class Administrador:
    def __init__(self, username, nombres, apellidos, dni, correo):
        self.username = username # FK a Usuario
        self.nombres = nombres
        self.apellidos = apellidos
        self.dni = dni
        self.correo = correo
        self.usuario = None

    @staticmethod
    def crear(admin):
        query = "INSERT INTO administrador (username, nombres, apellidos, dni, correo) VALUES (?, ?, ?, ?, ?)"
        params = (admin.username, admin.nombres, admin.apellidos, admin.dni, admin.correo)
        DB.execute(query, params)
        return True

    @staticmethod
    def obtener_por_username(username):
        query = "SELECT username, nombres, apellidos, dni, correo FROM administrador WHERE username = ?"
        params = (username,)
        row = DB.fetchone(query, params)
        if row:
            admin = Administrador(row[0], row[1], row[2], row[3], row[4])
            admin.usuario = Usuario.obtener_por_username(username)
            return admin
        return None
    
    @staticmethod
    def obtener_todos():
        query = "SELECT username, nombres, apellidos, dni, correo FROM administrador"
        result = DB.fetchall(query)
        administradores = []
        if result:
            for row in result:
                admin = Administrador(row[0], row[1], row[2], row[3], row[4])
                administradores.append(admin)
        return administradores

    @staticmethod
    def actualizar(admin):
        query = "UPDATE administrador SET nombres = ?, apellidos = ?, dni = ?, correo = ? WHERE username = ?"
        params = (admin.nombres, admin.apellidos, admin.dni, admin.correo, admin.username)
        DB.execute(query, params)
        return True

    @staticmethod
    def eliminar(username):
        query = "DELETE FROM administrador WHERE username = ?"
        params = (username,)
        DB.execute(query, params)
        return True