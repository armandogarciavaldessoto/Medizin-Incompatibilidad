import requests
from bs4 import BeautifulSoup

def extraer_seccion_ficha(nregistro, seccion):
    url = f"https://cima.aemps.es/cima/dochtml/ft/{nregistro}/{seccion}/FichaTecnica.html"
    res = requests.get(url)
    if res.status_code != 200:
        return f"❌ No se pudo acceder a la sección {seccion} para el registro {nregistro}.", None

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(res.content, "html.parser")
    texto = soup.get_text(separator="\n").strip()

    # Detectar encabezado sin contenido real
    if len(texto.splitlines()) <= 3 or "FICHA TECNICA" in texto.upper() and len(texto) < 100:
        # Enlace alternativo completo
        enlace_completo = f"https://cima.aemps.es/cima/dochtml/ft/{nregistro}/FichaTecnica.html"
        return None, enlace_completo

    return texto, None

