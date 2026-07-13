import streamlit as st
import requests
import time

params = st.query_params
prestador_alvo = params.get("prestador")

if not prestador_alvo:
    st.error("Link inválido.")
    st.stop()

# --- BLOCO DE SEGURANÇA (CÓDIGO SECRETO) ---
if 'acesso_autorizado' not in st.session_state:
    st.session_state.acesso_autorizado = False

if not st.session_state.acesso_autorizado:
    st.title("🔑 Acesso ao Karaoke")
    codigo_input = st.text_input("Digite o código secreto do evento:", type="password")
    if st.button("Validar Acesso"):
        if codigo_input == "1234": # DEFINE AQUI O TEU CÓDIGO SECRETO
            st.session_state.acesso_autorizado = True
            st.rerun()
        else:
            st.error("Código incorreto!")
    st.stop() # Bloqueia o restante do código até o código estar correto

# --- O RESTANTE DO SEU CÓDIGO CLIENTE VAI AQUI ---
# (Coloque aqui a parte de registro e pesquisa)
