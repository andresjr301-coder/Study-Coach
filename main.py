import streamlit as st
import openai
from PyPDF2 import PdfReader
import os

# --- ESTILO NEÓN Y MODO OSCURO ---
st.set_page_config(page_title="Campayo AI Mind", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    div.stButton > button:first-child {
        background-color: #1A1A1A;
        color: #00FF41;
        border: 2px solid #00FF41;
        border-radius: 5px;
        box-shadow: 0 0 10px #00FF41;
    }
    div.stButton > button:hover {
        background-color: #00FF41;
        color: black;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1A1A1A !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Configuración ---
st.sidebar.title("Configuración")
# Intentamos sacar la API Key de los Secrets de Streamlit o del input
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
api_key = api_key_input if api_key_input else st.secrets.get("OPENAI_API_KEY", "")

st.sidebar.divider()
st.sidebar.subheader("Mis Casilleros Mentales")
casilleros_input = st.sidebar.text_area("Formato: 1-Tea, 2-Noé...", 
                                      value="1-Té\n2-Noé\n3-Amo\n4-Oca\n5-Ola\n6-Oso\n7-Ufo\n8-Hacha\n9-Ave",
                                      height=200)

# --- FUNCIONES ---
def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

# --- INTERFAZ ---
st.title("🧠 Campayo AI: Entrenador de Mente Prodigiosa")

tabs = st.tabs(["📚 Procesar Temario", "🖼️ Video Mental", "📝 Test de Repaso"])

with tabs[0]:
    st.header("Sube tu temario")
    archivo_usuario = st.file_uploader("Sube el PDF de estudio", type=["pdf"])
    
    if archivo_usuario and api_key:
        if st.button("Aplicar Método Campayo"):
            with st.spinner("Analizando con sistema S.R.C..."):
                client = openai.OpenAI(api_key=api_key)
                texto_temario = extraer_texto_pdf(archivo_usuario)
                
                prompt = f"""
                Actúa como experto en el método de Ramón Campayo. 
                Analiza este temario: {texto_temario[:4000]}
                Usando estos casilleros: {casilleros_input}
                Genera: 1. RESUMEN S.R.C. 2. ASOCIACIONES INVEROSÍMILES para datos puros.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(response.choices[0].message.content)

with tabs[1]:
    st.header("Generador de Caricaturas")
    concepto = st.text_input("Dato a memorizar:")
    casillero = st.text_input("Casillero a usar:")
    
    if st.button("Crear Imagen Retro") and api_key:
        with st.spinner("Dibujando..."):
            client = openai.OpenAI(api_key=api_key)
            prompt_img = f"Simple 8-bit pixel art, black background, {concepto} interacting with {casillero}, retro game style."
            
            img_res = client.images.generate(
                model="dall-e-3",
                prompt=prompt_img,
                n=1,
                size="1024x1024"
            )
            st.image(img_res.data[0].url)

with tabs[2]:
    st.write("Sección de entrenamiento próximamente disponible.")
