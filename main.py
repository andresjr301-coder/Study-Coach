import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# Configuración de página
st.set_page_config(page_title="Campayo AI Free", layout="wide")

# --- ESTILO NEÓN ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #00FF41 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    .stTextInput>div>div>input {
        background-color: #1A1A1A !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    div.stButton > button {
        background-color: #1A1A1A;
        color: #00FF41;
        border: 2px solid #00FF41;
        box-shadow: 0 0 10px #00FF41;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Campayo AI: Edición Gratuita")

# Entrada manual de la llave para evitar errores de sistema
st.sidebar.title("Llave de Acceso")
api_key_groq = st.sidebar.text_input("Pega tu llave de Groq (gsk_...)", type="password")

if not api_key_groq:
    st.warning("⚠️ Por favor, pega tu llave 'gsk_...' en la barra lateral izquierda para comenzar.")
else:
    try:
        client = Groq(api_key=api_key_groq)
        
        archivo = st.file_uploader("Sube tu temario (PDF)", type=["pdf"])
        
        if archivo and st.button("🚀 Aplicar Método Campayo"):
            with st.spinner("Procesando con Llama 3..."):
                # Leer PDF
                reader = PdfReader(archivo)
                texto_completo = ""
                for page in reader.pages:
                    texto_completo += page.extract_text()
                
                # Pedir resumen a Groq
                prompt = f"Actúa como Ramón Campayo. Resume este temario y crea asociaciones inverosímiles para los datos difíciles: {texto_completo[:5000]}"
                
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.subheader("✅ Análisis Completado:")
                st.write(completion.choices[0].message.content)
    except Exception as e:
        st.error(f"Hubo un problema: {e}")
