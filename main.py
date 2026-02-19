import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import sqlite3

# --- CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="Campayo Multi-Tema", layout="wide")

def init_db():
    conn = sqlite3.connect('estudio_pro.db')
    c = conn.cursor()
    # Ahora guardamos por 'tema' en lugar de por 'nombre de archivo'
    c.execute('''CREATE TABLE IF NOT EXISTS temarios 
                 (tema TEXT, archivo TEXT, contenido TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ESTILO NEÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #00FF41 !important; font-family: 'Courier New', Courier, monospace !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #1A1A1A !important; color: #00FF41 !important; border: 1px solid #00FF41 !important; }
    div.stButton > button { background-color: #1A1A1A; color: #00FF41; border: 2px solid #00FF41; font-weight: bold; width: 100%; }
    div.stButton > button:hover { background-color: #00FF41; color: black; }
    </style>
    """, unsafe_allow_html=True)


# --- SIDEBAR: GESTIÓN DE TEMAS ---
st.sidebar.title("🗄️ BIBLIOTECA DE ESTUDIO")
api_key = st.sidebar.text_input("Llave Groq (gsk_...)", type="password")

st.sidebar.subheader("📥 Añadir a la Biblioteca")
nombre_tema = st.sidebar.text_input("Nombre del Tema (ej: Historia 1)")
nuevo_archivo = st.sidebar.file_uploader("Subir PDF", type=["pdf"])

if nuevo_archivo and nombre_tema:
    if st.sidebar.button("➕ Vincular al Tema"):
        reader = PdfReader(nuevo_archivo)
        texto = "".join([p.extract_text() for p in reader.pages])
        c = conn.cursor()
        c.execute("INSERT INTO temarios VALUES (?, ?, ?)", (nombre_tema.upper(), nuevo_archivo.name, texto))
        conn.commit()
        st.sidebar.success(f"'{nuevo_archivo.name}' añadido a {nombre_tema.upper()}")

# Selección de Tema (Agrupado)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT tema FROM temarios")
temas_disponibles = [fila[0] for fila in cursor.fetchall()]
tema_elegido = st.sidebar.selectbox("Selecciona qué tema estudiar hoy:", ["Ninguno"] + temas_disponibles)

if tema_elegido != "Ninguno":
    # Aquí ocurre la magia: Juntamos todos los archivos de ese tema
    cursor.execute("SELECT contenido FROM temarios WHERE tema=?", (tema_elegido,))
    todos_los_textos = [fila[0] for fila in cursor.fetchall()]
    st.session_state.texto_pdf = "\n\n--- NUEVA SECCIÓN/ARCHIVO ---\n\n".join(todos_los_textos)
    st.sidebar.info(f"📚 Estudiando {len(todos_los_textos)} archivos vinculados a {tema_elegido}")

st.sidebar.divider()
st.sidebar.subheader("📋 MIS CASILLEROS")
# Esta línea es la que crea el cuadro para que escribas tus casilleros
casilleros = st.sidebar.text_area(
    "Edita tu lista (Formato: 1-Té, 2-Noé...):", 
    value="1-Té, 2-Noé, 3-Amo, 4-Oca, 5-Ola, 6-Oso, 7-Ufo, 8-Hacha, 9-Ave, 10-Toro",
    height=200
)

# --- FUNCIÓN IA ---
def llamar_ai(prompt_sistema, mensaje_usuario):
    if not api_key: return "⚠️ Pega tu llave de Groq"
    try:
        client = Groq(api_key=api_key)
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": mensaje_usuario}],
            temperature=0.3, # Bajamos la temperatura para que sea más preciso y menos "creativo"
            max_tokens=3000
        )
        return res.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 CAMPAYO PRO: MEMORIA TOTAL")

if tema_elegido == "Ninguno":
    st.warning("👈 Sube un PDF o selecciona uno del historial en la barra lateral para comenzar.")
else:
    # Creamos las 4 pestañas
    tabs = st.tabs(["📝 SUPER RESUMEN", "💬 CHAT DE APOYO", "🧪 TEST CIEGO", "🎭 ASOCIACIONES"])

    with tabs[0]:
        st.header(f"Resumen Profundo: {tema_elegido}")
        if st.button("🚀 Generar Resumen Exhaustivo"):
            with st.spinner("Analizando cada detalle..."):
                prompt_sys = "Eres Ramón Campayo. Extrae TODOS los puntos clave, fechas y nombres del temario."
                res = llamar_ai(prompt_sys, st.session_state.texto_pdf[:10000])
                st.markdown(res)

    with tabs[1]:
        st.header(f"Chat Contextual sobre {tema_elegido}")
        if "chat_pro" not in st.session_state: st.session_state.chat_pro = []
        for m in st.session_state.chat_pro:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if p := st.chat_input("Pregunta sobre este tema..."):
            st.session_state.chat_pro.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            resp = llamar_ai(f"Basado en estos documentos: {st.session_state.texto_pdf[:6000]}", p)
            with st.chat_message("assistant"): st.markdown(resp)
            st.session_state.chat_pro.append({"role": "assistant", "content": resp})

    with tabs[2]:
        st.header("🧪 Test de Autoevaluación")
        if st.button("🎲 Generar Nueva Pregunta"):
            prompt_sys = "Genera una pregunta difícil. Indica opciones A, B y C. Pon ---SOLUCIÓN--- al final."
            st.session_state.pregunta_test = llamar_ai(prompt_sys, st.session_state.texto_pdf[:7000])
        
        if "pregunta_test" in st.session_state:
            partes = st.session_state.pregunta_test.split("---SOLUCIÓN---")
            st.markdown(partes[0])
            col_a, col_b, col_c = st.columns(3)
            with col_a: 
                if st.button("Elegir A"): st.toast("¿Será la A?")
            with col_b: 
                if st.button("Elegir B"): st.toast("¿Será la B?")
            with col_c: 
                if st.button("Elegir C"): st.toast("¿Será la C?")
            with st.expander("👁️ VER RESPUESTA CORRECTA"):
                if len(partes) > 1: st.success(partes[1])

    with tabs[3]:
        st.header("🎭 Laboratorio de Asociaciones")
        with st.expander("📚 Ver mis Casilleros Mentales"):
            st.write(casilleros)
        dato = st.text_input("Dato difícil de este tema:")
        if st.button("✨ Crear Historia Increíble"):
            prompt_sys = f"Experto en mnemotecnia. Usa estos casilleros: {casilleros}"
            res = llamar_ai(prompt_sys, f"Crea una asociación para: {dato} usando el contexto de {tema_elegido}")
            st.success(res)
