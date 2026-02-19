import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

st.set_page_config(page_title="Campayo Total Mind", layout="wide")

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
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #00FF41;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE MEMORIA (Session State) ---
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR ---
st.sidebar.title("🛠️ CONFIGURACIÓN")
api_key = st.sidebar.text_input("Llave Groq (gsk_...)", type="password")
st.sidebar.divider()
casilleros = st.sidebar.text_area("📋 MIS CASILLEROS", 
                                 value="1-Té, 2-Noé, 3-Amo, 4-Oca, 5-Ola, 6-Oso, 7-Ufo, 8-Hacha, 9-Ave, 10-Toro")

def llamar_ai(prompt_sistema, mensaje_usuario):
    if not api_key:
        st.error("⚠️ Falta la llave de Groq")
        return ""
    try:
        client = Groq(api_key=api_key)
        res = client.chat.completions.create(
            # Cambiamos a este que es el más estable actualmente
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.5,
            max_tokens=2048 # Esto ayuda a que los resúmenes no se corten
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Error de conexión: {e}"
# --- INTERFAZ ---
st.title("🧠 CAMPAYO TOTAL MIND STATION")

tabs = st.tabs(["📂 SUBIR Y RESUMIR", "💬 CHAT CONTEXTUAL", "🧪 TEST INTERACTIVO", "🎭 ASOCIACIONES"])

with tabs[0]:
    st.header("Carga de Conocimiento")
    archivo = st.file_uploader("Sube el PDF que será el cerebro de la app", type=["pdf"])
    
    if archivo:
        if st.button("🧠 Procesar y Memorizar PDF"):
            with st.spinner("Leyendo y analizando..."):
                reader = PdfReader(archivo)
                st.session_state.texto_pdf = "".join([p.extract_text() for p in reader.pages])
                st.success("¡PDF cargado con éxito! Ahora todas las pestañas conocen este contenido.")
    
    if st.session_state.texto_pdf:
        if st.button("📝 Generar Gran Resumen Detallado"):
            with st.spinner("Redactando resumen extenso..."):
                prompt_sys = "Eres Ramón Campayo. Crea un resumen MUY extenso, detallado y estructurado por puntos clave."
                res = llamar_ai(prompt_sys, f"Analiza y resume a fondo este texto: {st.session_state.texto_pdf[:8000]}")
                st.markdown(res)

with tabs[1]:
    st.header("Chat Inteligente (Sobre tu PDF)")
    if not st.session_state.texto_pdf:
        st.info("Sube un PDF en la primera pestaña para chatear sobre él.")
    else:
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if p := st.chat_input("Dime, ¿qué parte del PDF no entiendes?"):
            st.session_state.chat_history.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            
            prompt_sys = f"Eres Ramón Campayo. Responde dudas basándote exclusivamente en este PDF: {st.session_state.texto_pdf[:5000]}"
            resp = llamar_ai(prompt_sys, p)
            
            with st.chat_message("assistant"): st.markdown(resp)
            st.session_state.chat_history.append({"role": "assistant", "content": resp})

with tabs[2]:
    st.header("Entrenamiento Tipo Test")
    if st.session_state.texto_pdf:
        if st.button("🎲 Generar Nueva Pregunta de Examen"):
            prompt_sys = "Genera UNA pregunta tipo test difícil sobre el PDF. Formato: Pregunta | A) opción | B) opción | C) opción | Respuesta Correcta | Explicación."
            pregunta_data = llamar_ai(prompt_sys, st.session_state.texto_pdf[:5000])
            st.session_state.pregunta_actual = pregunta_data
        
        if "pregunta_actual" in st.session_state:
            st.markdown(st.session_state.pregunta_actual)
            col1, col2, col3 = st.columns(3)
            with col1: 
                if st.button("Opción A"): st.info("Revisa la solución en la explicación arriba.")
            with col2: 
                if st.button("Opción B"): st.info("Revisa la solución en la explicación arriba.")
            with col3: 
                if st.button("Opción C"): st.info("Revisa la solución en la explicación arriba.")
    else:
        st.warning("Primero sube un PDF.")

with tabs[3]:
    st.header("Asociaciones Contextuales")
    dato_raro = st.text_input("Dato difícil del PDF a memorizar:")
    if st.button("✨ Crear Historia Increíble"):
        if st.session_state.texto_pdf:
            prompt_sys = f"Usa el contexto del PDF ({st.session_state.texto_pdf[:2000]}) y estos casilleros ({casilleros})."
            res = llamar_ai(prompt_sys, f"Crea una asociación inverosímil para: {dato_raro}")
            st.success(res)
        else:
            st.error("Sube el PDF para que la asociación sea contextual.")
