import pandas as pd
import os
import time
from datetime import datetime
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
def cargar_o_descargar_medicamentos():
    csv_path = "medicamentos_cima.csv"

    # Si no existe o tiene más de 1 día (86400 segundos), descargar
    if not os.path.exists(csv_path) or (time.time() - os.path.getmtime(csv_path)) > 86400:
        df = descargar_medicamentos()
        df.to_csv(csv_path, index=False)
    else:
        df = pd.read_csv(csv_path)

    return df
