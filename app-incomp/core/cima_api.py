import os
import time
import pandas as pd
import requests
import streamlit as st

BASE_URL = "https://cima.aemps.es/cima/rest/"

def descargar_medicamentos():
    pagina = 1
    todos = []
    while True:
        params = {"pagina": pagina}
        res = requests.get(BASE_URL + "medicamentos", params=params)
        if res.status_code != 200:
            break
        resultados = res.json().get("resultados", [])
        if not resultados:
            break
        todos.extend(resultados)
        pagina += 1
    return pd.DataFrame(todos)

@st.cache_data
def cargar_datos_seguro():
    csv_path = "medicamentos_cima.csv"

    # Detectar si estamos en Streamlit Cloud (headless server)
    en_cloud = "STREAMLIT_SERVER_HEADLESS" in os.environ

    if en_cloud:
        # Solo cargar el CSV ya incluido en el repositorio
        return pd.read_csv(csv_path)
    else:
        # Local: usar CSV si existe y es reciente, si no, descargar
        if not os.path.exists(csv_path) or (time.time() - os.path.getmtime(csv_path)) > 86400:
            df = descargar_medicamentos()
            df.to_csv(csv_path, index=False)
        else:
            df = pd.read_csv(csv_path)
        return df
