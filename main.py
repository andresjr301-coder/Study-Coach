import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

st.set_page_config(page_title="Campayo AI Free", layout="wide")

# (Aquí mantén el bloque de ESTILO NEÓN que ya tienes)

st.title("🧠 Campayo AI: Edición Gratuita")

# Configuración en la barra lateral
st.sidebar.title("Configuración")
api_key = st.sidebar.text_input("Groq API Key (gsk_...)", type="password")

if not api_key:
    st.info("Por favor, introduce tu llave gratuita de Groq para empezar.")
else:
    client = Groq(api_key=api_key)
    
    archivo = st.file_uploader("Sube tu PDF", type=["pdf"])
    
    if archivo and st.button("Aplicar Método Campayo"):
        reader = PdfReader(archivo)
        texto = "".join([page.extract_text() for page in reader.pages])
        
        # Usamos Llama 3 (Gratis y potente)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Resume este texto usando el método de Ramón Campayo: {texto[:5000]}",
                }
            ],
            model="llama3-8b-8192",
        )
        st.markdown(chat_completion.choices[0].message.content)
