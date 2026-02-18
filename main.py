import streamlit as st
import openai
from PyPDF2 import PdfReader
import os
# --- ESTILO NEÓN Y MODO OSCURO ---
st.markdown("""
    <style>
    /* Fondo total de la app */
    .stApp {
        background-color: #050505;
    }
    
    /* Texto en verde neón */
    h1, h2, h3, p, span, label {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }

    /* Estilo para los botones */
    div.stButton > button:first-child {
        background-color: #1A1A1A;
        color: #00FF41;
        border: 2px solid #00FF41;
        border-radius: 5px;
        box-shadow: 0 0 10px #00FF41;
        font-weight: bold;
    }

    div.stButton > button:hover {
        background-color: #00FF41;
        color: black;
    }

    /* Estilo para los inputs de texto */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1A1A1A !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }

    /* Línea divisoria neón */
    hr {
        border: 1px solid #00FF41 !important;
    }
    </style>
    """, unsafe_allow_html=True)
# Configuración de la página
st.set_page_config(page_title="Campayo AI Mind", layout="wide")

# --- SIDEBAR: Configuración y Casilleros ---
st.sidebar.title("Configuración")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if api_key:
    openai.api_key = api_key

st.sidebar.divider()
st.sidebar.subheader("Mis Casilleros Mentales")
casilleros_input = st.sidebar.text_area("Formato: 1-Tea, 2-Noé...", height=200, 
                                      help="Introduce aquí tus casilleros para que la IA los use.")

# --- FUNCIONES DE APOYO ---
def extraer_texto_pdf(file):
    reader = PdfReader(file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text()
    return texto

# --- INTERFAZ PRINCIPAL ---
st.title("🧠 Campayo AI: Entrenador de Mente Prodigiosa")

tabs = st.tabs(["📚 Procesar Temario", "🖼️ Vídeo Mental (Pixel-Art)", "📝 Test de Repaso"])

with tabs[0]:
    st.header("Sube tu temario")
    archivo_usuario = st.file_uploader("Sube el PDF de lo que quieres estudiar", type=["pdf"])
    
    if archivo_usuario and api_key:
        if st.button("Aplicar Método Campayo"):
            with st.spinner("Analizando temario con el sistema S.R.C..."):
                texto_temario = extraer_texto_pdf(archivo_usuario)
                
                # Prompt para la IA
                prompt = f"""
                Actúa como experto en el método de Ramón Campayo. 
                Analiza este temario: {texto_temario[:4000]}
                
                Usando estos casilleros: {casilleros_input}
                
                Genera:
                1. RESUMEN: De lo general a lo particular (S.R.C).
                2. MAPA MENTAL: Crea un código Mermaid.js para visualizarlo.
                3. ASOCIACIONES: Crea 3 asociaciones inverosímiles para los puntos más difíciles usando mis casilleros.
                """
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                resultado = response.choices[0].message.content
                st.markdown(resultado)

with tabs[1]:
    st.header("Generador de Caricaturas Mnemotécnicas")
    concepto = st.text_input("¿Qué concepto o dato quieres visualizar?")
    casillero_a_usar = st.text_input("¿Qué casillero vas a usar?")
    
    if st.button("Generar Imagen Pixel-Art") and api_key:
        with st.spinner("Dibujando tu vídeo mental..."):
            prompt_imagen = f"Simple 8-bit pixel art, line drawing, console game style, white background, {concepto} interactuando de forma absurda con {casillero_a_usar}, high contrast."
            
            img_response = openai.Image.create(
                prompt=prompt_imagen,
                n=1,
                size="512x512"
            )
            st.image(img_response['data'][0]['url'], caption="Tu asociación visual estilo retro")

with tabs[2]:
    st.header("Entrenamiento y Repasos")
    st.write("Aquí se generarán los cuestionarios basados en tu temario.")
    if st.button("Crear Test Rápido"):
        st.info("Funcionalidad: La IA leerá el texto procesado y te hará preguntas tipo test.")
