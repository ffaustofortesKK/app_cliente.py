import streamlit as st
import requests
import time
from supabase import create_client

# Configuração Supabase (O cliente precisa de consultar a lista de músicas)
url = st.secrets["URL_SUPABASE"]
key = st.secrets["KEY_SUPABASE"]
supabase = create_client(url, key)

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

# Captura o prestador da URL
query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")
URL_FIREBASE_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"

if 'registado' not in st.session_state: st.session_state.registado = False

if not st.session_state.registado:
    st.subheader("🎤 Registo do Cantor")
    nome = st.text_input("Seu nome:")
    if st.button("Entrar no Karaokê"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # BUSCA AUTOMÁTICA NO SUPABASE (Lista de Músicas)
    # Isso garante que o cliente só peça músicas que você realmente tem!
    try:
        res = supabase.table("musicas").select("nome").execute()
        lista_musicas = [m["nome"] for m in res.data] if res.data else []
    except:
        lista_musicas = []

    st.subheader("🔍 Escolha a sua música")
    busca = st.selectbox("Pesquise e selecione sua música:", [""] + lista_musicas)

    if busca and st.button("🎤 Confirmar Pedido"):
        requests.post(URL_FIREBASE_PEDIDOS, json={
            "cantor": st.session_state.nome, 
            "musica": busca
        })
        st.success(f"Pedido de '{busca}' enviado com sucesso!")
        time.sleep(2)
        st.rerun()

    st.divider()
    if st.button("Sair/Trocar Cantor"): 
        st.session_state.registado = False
        st.rerun()
