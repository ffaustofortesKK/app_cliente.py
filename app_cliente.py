import streamlit as st
import requests
import time

# --- CONFIGURAÇÕES ---
URL_FIREBASE_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

st.set_page_config(page_title="FF KARAOKE CLOUD", layout="wide")

# Captura o prestador da URL: app/?prestador=nome-do-prestador
query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")
URL_FIREBASE_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"

if 'registado' not in st.session_state: st.session_state.registado = False

if not st.session_state.registado:
    st.subheader("📝 Registo Inicial")
    nome = st.text_input("Nome:")
    if st.button("Concluir Registo"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    busca = st.text_input("🔍 Pesquisar Música:")
    escolha = None
    if busca:
        try:
            dados = requests.get(URL_FIREBASE_CATALOGO, timeout=5).json()
            resultados = [m for m in dados if busca.lower() in m.lower()]
            escolha = st.selectbox("Selecione:", resultados)
        except: pass

    if escolha and st.button("Confirmar Pedido"):
        requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": escolha})
        st.success("Pedido enviado!")
        time.sleep(1); st.rerun()

    # Pedido manual
    pedido_manual = st.text_input("Não achou? Digite a música:")
    if st.button("Confirmar Pedido Manual") and pedido_manual:
        requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": pedido_manual})
        st.success("Pedido enviado!")
        st.rerun()

    if st.button("Sair"): st.session_state.registado = False; st.rerun()
