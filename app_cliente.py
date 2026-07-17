import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

if 'registado' not in st.session_state: st.session_state.registado = False
if 'minha_playlist' not in st.session_state: st.session_state.minha_playlist = []

query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{prestador_slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"
URL_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

@st.cache_data(ttl=60)
def obter_catalogo():
    try:
        res = requests.get(URL_CATALOGO).json()
        return list(res.values()) if isinstance(res, dict) else (res or [])
    except: return []

if not st.session_state.registado:
    st.title("🎤 FF Karaoke")
    nome = st.text_input("Como quer ser chamado?")
    if st.button("Entrar"):
        if nome: st.session_state.nome = nome; st.session_state.registado = True; st.rerun()
else:
    status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
    
    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    comando = status.get("comando", "")

    if nome_firebase == meu_nome and comando == "aguardando_play":
        st.success("🎉 É a sua vez!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
    elif nome_firebase == meu_nome and comando == "play":
        st.info("🎤 Música a tocar na TV!")
    else:
        st.info("Prepare a sua playlist!")
        # [A lógica de playlist e pesquisa permanece a mesma]
        termo = st.text_input("🔍 Pesquisar:")
        resultados = [m for m in obter_catalogo() if termo.lower() in str(m).lower()] if termo else []
        if termo and resultados:
            musica_sel = st.selectbox("Escolha:", resultados)
            if st.button("➕ Adicionar"): st.session_state.minha_playlist.append(musica_sel); st.rerun()
        
        if st.button("🚀 Enviar Pedidos"):
            for m in st.session_state.minha_playlist:
                requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": m})
            st.session_state.minha_playlist = []
            st.rerun()

    st.divider()
    if st.button("Sair"): st.session_state.registado = False; st.rerun()
    time.sleep(2); st.rerun()
