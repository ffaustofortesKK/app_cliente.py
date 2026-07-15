import streamlit as st
import requests

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

# Captura o prestador da URL
query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")
URL_FIREBASE_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"
# URL do catálogo (onde você vai listar as músicas no Firebase)
URL_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

if 'registado' not in st.session_state: st.session_state.registado = False

if not st.session_state.registado:
    nome = st.text_input("Seu nome:")
    if st.button("Entrar"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # Busca a lista de músicas diretamente do Firebase (sem precisar de Supabase)
    try:
        res = requests.get(URL_CATALOGO).json()
        lista_musicas = res if res else []
    except:
        lista_musicas = ["Erro ao carregar catálogo"]

    busca = st.selectbox("Escolha sua música:", [""] + lista_musicas)

    if busca and st.button("🎤 Confirmar Pedido"):
        requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": busca})
        st.success("Pedido enviado!")
        st.rerun()

    if st.button("Sair"): st.session_state.registado = False; st.rerun()
