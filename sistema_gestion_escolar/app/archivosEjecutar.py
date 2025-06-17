from werkzeug.security import generate_password_hash
# Cambia 'tu_contrasena_segura_aqui' por una contraseña robusta que vayas a usar.
hashed_password = generate_password_hash('admin')
print(hashed_password)