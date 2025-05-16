import pandas as pd

def inicializar_historial():
    return []

def registrar(historial, med1, med2, resultado, tipo="nombre o principio activo"):
    historial.append({
        "Medicamento 1": med1,
        "Medicamento 2": med2,
        "Resultado": resultado,
        "Tipo": tipo
    })

def mostrar(historial):
    return pd.DataFrame(historial)
