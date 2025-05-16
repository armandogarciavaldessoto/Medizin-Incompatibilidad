import streamlit as st
from itertools import combinations
import pandas as pd

from core.cima_api import cargar_o_descargar_medicamentos
from core.fichas import extraer_seccion_ficha
from core.comparador import obtener_nregistro, comparar_mencion
from core.comparador import obtener_pactivos
from core.riesgos import evaluar_riesgos
from core.historial import inicializar_historial, registrar, mostrar

st.set_page_config(page_title="Incompatibilidades CIMA", layout="wide")

df = cargar_o_descargar_medicamentos()

# Estilo personalizado: verde, azul, blanco
st.markdown("""
    <style>
    /* Fondo y texto base */
    body, .stApp {
        background-color: #ffffff;
        color: #003366;
    }

    /* Títulos y etiquetas */
    h1, h2, h3, .stMarkdown, .stText, .stSelectbox label {
        color: #003366 !important;
        font-weight: 700;
    }

    /* Selector de medicamentos */
    .stSelectbox > div {
        border-top: 2px solid white !important;
    }

    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[role="button"],
    .stSelectbox div[role="listbox"] {
        color: #003366 !important;
        background-color: white !important;
    }

    /* Botón */
    .stButton>button {
        background-color: #2ecc71;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1.2em;
        font-size: 1rem;
    }

    .stButton>button:disabled {
        background-color: #a8d5b7;
        color: white;
    }

    .stButton>button:hover {
        background-color: #27ae60;
        color: white;
    }

    /* Área de texto (fichas técnicas) */
    .stTextArea textarea {
        background-color: #f9f9f9;
        color: #003366;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
    }

    /* Enlaces */
    .stMarkdown a {
        color: #003366;
        font-weight: bold;
        text-decoration: underline;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f1f8f6;
    }

    /* Color negro para menú lateral radio */
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stRadio div {
        color: #000000 !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


# Carga de datos
st.session_state["medicamentos_cima"] = cargar_o_descargar_medicamentos()
df = st.session_state["medicamentos_cima"]
lista_nombres = sorted(df["nombre"].unique())

# Historial en sesión
if "historial" not in st.session_state:
    st.session_state["historial"] = inicializar_historial()

# Sidebar
st.title("💊 Sistema de Incompatibilidades de Medicamentos")
opcion = st.sidebar.radio(
    label="📚 Elige una funcionalidad:",
    options=[
        "📄 Ver sección 4.5 (interacciones)",
        "🚫 Ver sección 4.3 (contraindicaciones)",
        "🔍 Comparar 2 medicamentos",
        "📋 Comparar lista de medicamentos",
        "⚠️ Ver etiquetas de riesgo",
        "📜 Historial de comparaciones"
    ],
    label_visibility="visible"
)

if opcion == "📄 Ver sección 4.5 (interacciones)":
    st.subheader("📄 Sección 4.5: Interacciones")

    # Filtros laboratorio + medicamento
    labs = sorted(df["labtitular"].dropna().unique())
    lab_45 = st.selectbox("🔬 Filtrar por laboratorio:", labs, key="lab_45")
    df_45 = df[df["labtitular"] == lab_45]
    meds_45 = sorted(df_45["nombre"].unique())
    seleccion = st.selectbox("Selecciona un medicamento:", meds_45)

    if st.button("Ver sección 4.5"):
        nreg, _ = obtener_nregistro(seleccion, df_45)
        if not nreg:
            st.error("No se encontró el medicamento.")
        else:
            texto, enlace = extraer_seccion_ficha(nreg, "4.5")
            if texto:
                st.text_area("Contenido de la sección 4.5", texto, height=400)
            else:
                st.warning("⚠️ La sección 4.5 no está disponible en formato segmentado para este medicamento.")
                st.markdown(f"[📄 Ver ficha técnica completa en CIMA]({enlace})")

# 2. Ver sección 4.3
elif opcion == "🚫 Ver sección 4.3 (contraindicaciones)":
    st.subheader("🚫 Sección 4.3: Contraindicaciones")

    # Selector por laboratorio
    labs = sorted(df["labtitular"].dropna().unique())
    lab_43 = st.selectbox("🔬 Filtrar por laboratorio:", labs, key="lab_43")

    # Selector de medicamento filtrado
    df_43 = df[df["labtitular"] == lab_43]
    meds_43 = sorted(df_43["nombre"].unique())
    seleccion = st.selectbox("Selecciona un medicamento:", meds_43, key="contraindicaciones")

    if st.button("Ver sección 4.3"):
        nreg, _ = obtener_nregistro(seleccion, df_43)
        if not nreg:
            st.error("❌ No se encontró el medicamento.")
        else:
            texto, enlace = extraer_seccion_ficha(nreg, "4.3")
            if texto:
                st.text_area("Contenido de la sección 4.3", texto, height=400)
            else:
                st.warning("⚠️ La sección 4.3 no está disponible en formato segmentado para este medicamento.")
                st.markdown(f"[📄 Ver ficha técnica completa en CIMA]({enlace})")


# 3. Comparar dos medicamentos
elif opcion == "🔍 Comparar 2 medicamentos":
    st.subheader("🔍 Comparar dos medicamentos")
    col1, col2 = st.columns(2)

    with col1:
        lab1 = st.selectbox("Laboratorio para Medicamento 1", sorted(df["labtitular"].dropna().unique()), key="lab_m1")
        meds1 = sorted(df[df["labtitular"] == lab1]["nombre"].unique())
        med1 = st.selectbox("Medicamento 1", meds1, key="comp1")

    with col2:
        lab2 = st.selectbox("Laboratorio para Medicamento 2", sorted(df["labtitular"].dropna().unique()), key="lab_m2")
        meds2 = sorted(df[df["labtitular"] == lab2]["nombre"].unique())
        med2 = st.selectbox("Medicamento 2", meds2, key="comp2")

    if st.button("Comparar medicamentos"):
        if med1 == med2:
            st.warning("Selecciona dos medicamentos diferentes.")
        else:
            res1 = comparar_mencion(med1, med2, df)
            res2 = comparar_mencion(med2, med1, df)
            st.markdown(f"**{med1} ➡️ {med2}:** {res1}")
            st.markdown(f"**{med2} ➡️ {med1}:** {res2}")
            registrar(st.session_state["historial"], med1, med2, res1)
            registrar(st.session_state["historial"], med2, med1, res2)

# 4. Comparar lista
elif opcion == "📋 Comparar lista de medicamentos":
    st.subheader("📋 Comparar múltiples medicamentos")
    lab_lista = st.selectbox("🔬 Filtrar por laboratorio:", sorted(df["labtitular"].dropna().unique()), key="lab_lista")
    df_lista = df[df["labtitular"] == lab_lista]
    meds_lista = sorted(df_lista["nombre"].unique())
    seleccion = st.multiselect("Selecciona al menos dos medicamentos", meds_lista)

    if st.button("Analizar lista"):
        if len(seleccion) < 2:
            st.warning("Selecciona al menos dos medicamentos.")
        else:
            for m1, m2 in combinations(seleccion, 2):
                res1 = comparar_mencion(m1, m2, df)
                res2 = comparar_mencion(m2, m1, df)
                st.markdown(f"### {m1} ↔ {m2}")
                if "se menciona" in res1.lower() or "principio activo" in res1.lower():
                    st.error(f"➡️ {res1}")
                if "se menciona" in res2.lower() or "principio activo" in res2.lower():
                    st.error(f"⬅️ {res2}")
                if all(k not in res1.lower() + res2.lower() for k in ["se menciona", "principio activo"]):
                    st.success("🟢 Sin incompatibilidades aparentes")
                registrar(st.session_state["historial"], m1, m2, res1)
                registrar(st.session_state["historial"], m2, m1, res2)
                st.markdown("---")

# 5. Ver etiquetas de riesgo
elif opcion == "⚠️ Ver etiquetas de riesgo":
    st.subheader("⚠️ Indicadores de riesgo")
    lab_riesgo = st.selectbox("🔬 Filtrar por laboratorio:", sorted(df["labtitular"].dropna().unique()), key="lab_riesgos")
    df_riesgo = df[df["labtitular"] == lab_riesgo]
    meds_riesgo = sorted(df_riesgo["nombre"].unique())
    seleccion = st.selectbox("Selecciona un medicamento:", meds_riesgo, key="riesgos")

    if st.button("Ver riesgos"):
        riesgos = evaluar_riesgos(seleccion, df)
        if riesgos:
            for r in riesgos:
                st.warning(r)
        else:
            st.success("✅ Sin indicadores de riesgo especiales.")

# 6. Ver historial
elif opcion == "📜 Historial de comparaciones":
    st.subheader("📜 Comparaciones registradas en esta sesión")
    historial_df = mostrar(st.session_state["historial"])
    if historial_df.empty:
        st.info("📭 Aún no se han hecho comparaciones.")
    else:
        st.dataframe(historial_df, use_container_width=True)
