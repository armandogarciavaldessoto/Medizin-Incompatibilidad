from .fichas import extraer_seccion_ficha
from .cima_api import descargar_medicamentos

def obtener_nregistro(nombre, df):
    filtro = df[df["nombre"].str.lower().str.contains(nombre.lower())]
    if filtro.empty:
        return None
    return filtro.iloc[0]["nregistro"], filtro.iloc[0]["nombre"]

def obtener_pactivos(nombre, df):
    nreg, _ = obtener_nregistro(nombre, df)
    if not nreg:
        return []
    fila = df[df["nregistro"] == nreg]
    if fila.empty or "pactivos" not in fila.columns:
        return []
    return [p.strip().lower() for p in fila.iloc[0]["pactivos"].split(",")]

def comparar_mencion(med1, med2, df):
    nreg1, _ = obtener_nregistro(med1, df)
    texto = extraer_seccion_ficha(nreg1, "4.5")
    if med2.lower() in texto.lower():
        return f"⚠️ '{med2}' se menciona en ficha de '{med1}'."
    for pa in obtener_pactivos(med2, df):
        if pa in texto.lower():
            return f"⚠️ Principio activo '{pa}' de '{med2}' se menciona en ficha de '{med1}'."
    return f"✅ Ninguna mención de '{med2}' en ficha de '{med1}'."
