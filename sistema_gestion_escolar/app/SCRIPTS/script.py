import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re

# Configuración
BASE_URL = "https://grupociencias.edu.pe"
VISITED = set()
OUTPUT_DIR = "paginas_txt"
MAX_PAGINAS = 500  # Por si deseas limitar (ajustable)

# Crear carpeta de salida
os.makedirs(OUTPUT_DIR, exist_ok=True)

def limpiar_nombre_archivo(url):
    """Genera un nombre válido para guardar el archivo"""
    parsed = urlparse(url)
    nombre = parsed.path.strip("/").replace("/", "_")
    if not nombre:
        nombre = "index"
    if parsed.query:
        nombre += "_" + re.sub(r'[=&]', "_", parsed.query)
    return nombre + ".txt"

def es_url_valida(url):
    """Verifica si pertenece al mismo dominio"""
    parsed = urlparse(url)
    return parsed.scheme.startswith("http") and urlparse(BASE_URL).netloc in parsed.netloc

def guardar_html_como_txt(url, html):
    """Guarda el HTML como texto plano"""
    nombre_archivo = limpiar_nombre_archivo(url)
    ruta = os.path.join(OUTPUT_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[✔] HTML guardado: {ruta}")

def analizar_url(url):
    """Visita la URL, guarda el HTML y sigue los enlaces internos"""
    if url in VISITED or len(VISITED) >= MAX_PAGINAS:
        return
    try:
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code != 200 or 'text/html' not in respuesta.headers.get("Content-Type", ""):
            return

        html = respuesta.text
        guardar_html_como_txt(url, html)
        VISITED.add(url)

        soup = BeautifulSoup(html, "html.parser")
        enlaces = soup.find_all("a", href=True)
        for enlace in enlaces:
            nueva_url = urljoin(url, enlace['href'])
            nueva_url = nueva_url.split("#")[0]  # Elimina fragmentos
            if es_url_valida(nueva_url) and nueva_url not in VISITED:
                analizar_url(nueva_url)

    except Exception as e:
        print(f"[⚠] Error al procesar {url}: {e}")

# Inicio del rastreo
analizar_url(BASE_URL)



