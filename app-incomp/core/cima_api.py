import requests
import pandas as pd

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
