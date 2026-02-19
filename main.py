import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

st.set_page_config(page_title="Campayo Mind Station", layout="wide")

# --- ESTILO NEÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1A1A1A !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    div.stButton > button {
        background-color: #1A1A1A;
        color: #00FF41;
        border: 2px solid #00FF41;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🛠️ PANEL DE CONTROL")
api_key = st.sidebar.text_input("Llave Groq (gsk_...)", type="password")

st.sidebar.divider()
st.sidebar.subheader("📋 MIS CASILLEROS")
mis_casilleros = st.sidebar.text_area("Personaliza tus casilleros aquí:", 
                                     value="1-Té, 2-Noé, 3-Amo, 4-Oca, 5-Ola, 6-Oso, 7-Ufo, 8-Hacha, 9-Ave, 10-Toro")

# --- FUNCIONES ---
def llamar_ai(prompt):
    if not api_key:
        st.error("Pega tu llave en la barra lateral")
        return ""
    client = Groq(api_key=api_key)
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 CAMPAYO MIND STATION")

tabs = st.tabs(["📚 PDF & TEST", "💬 CHAT DE ESTUDIO", "🎭 ASOCIACIONES"])

with tabs[0]:
    st.header("Estudio con PDF")
    archivo = st.file_uploader("Sube tu temario", type=["pdf"])
    if archivo:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Generar Resumen Campayo"):
                reader = PdfReader(archivo)
                texto = "".join([p.extract_text() for p in reader.pages])
                res = llamar_ai(f"Resume este texto como Ramón Campayo: {texto[:4000]}")
                st.write(res)
        with col2:
            if st.button("❓ Crear Test de Examen"):
                reader = PdfReader(archivo)
                texto = "".join([p.extract_text() for p in reader.pages])
                res = llamar_ai(f"Crea 3 preguntas tipo test con opciones y soluciones sobre: {texto[:4000]}")
                st.write(res)

with tabs[1]:
    st.header("Chat con tu Instructor")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Pregúntame cualquier duda..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        respuesta = llamar_ai(f"Eres Ramón Campayo. Responde dudas de estudio: {prompt}")
        with st.chat_message("assistant"):
            st.markdown(respuesta)
        st.session_state.messages.append({"role": "assistant", "content": respuesta})

with tabs[2]:
    st.header("Generador de Imágenes Mentales")
    st.write("Convierte datos fríos en historias locas e inolvidables.")
    dato = st.text_input("¿Qué dato quieres memorizar? (Ej: 1492, Mitocondria...)")
    if st.button("🔥 Crear Asociación Inverosímil"):
        contexto = f"Usa estos casilleros si es necesario: {mis_casilleros}"
        res = llamar_ai(f"Como Ramón Campayo, crea una asociación inverosímil, ridícula y con movimiento para memorizar: {dato}. {contexto}")
        st.success(res)
