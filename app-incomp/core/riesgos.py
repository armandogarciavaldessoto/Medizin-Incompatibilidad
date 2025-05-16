def evaluar_riesgos(med, df):
    nregistro = df[df["nombre"] == med]["nregistro"].values[0]
    fila = df[df["nregistro"] == nregistro].iloc[0]
    riesgos = []
    if fila.get("triangulo"): riesgos.append("🔺 Triángulo negro")
    if fila.get("huerfano"): riesgos.append("🧬 Medicamento huérfano")
    if fila.get("receta"): riesgos.append("📄 Requiere receta")
    if fila.get("conduc"): riesgos.append("🚗 Afecta a conducción")
    if not fila.get("comerc"): riesgos.append("⚠️ No comercializado")
    return riesgos
