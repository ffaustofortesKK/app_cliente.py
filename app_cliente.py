import streamlit as st
import requests
import time

st.set_page_config(page_title="FF Karaoke", layout="centered")

# Captura o parâmetro da URL
query_params = st.query_params
prestador_alvo = query_params.get("prestador")

# Se o parâmetro não existir na URL, ele mostrará um erro amigável
if not prestador_alvo:
    st.error("❌ Link inválido!")
    st.info("Por favor, acesse através do QR Code ou link fornecido pelo prestador.")
    st.stop()

# --- BLOCO DE SEGURANÇA ---
if 'acesso_autorizado' not in st.session_state:
    st.session_state.acesso_autorizado = False

if not st.session_state.acesso_autorizado:
    st.title("🔑 Acesso ao Karaoke")
    codigo_input = st.text_input("Digite o código secreto do evento:", type="password")
    if st.button("Validar Acesso"):
        if codigo_input == "1234":
            st.session_state.acesso_autorizado = True
            st.rerun()
        else:
            st.error("Código incorreto!")
    st.stop()

# --- SE O CÓDIGO ESTIVER CORRETO, CONTINUA AQUI ---
st.success(f"Conectado ao evento de: {prestador_alvo}")
# ... (restante do código de pesquisa)
