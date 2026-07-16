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

@st.cache_data(ttl=300)
def obter_catalogo():
    try:
        res = requests.get(URL_CATALOGO).json()
        return list(res.values()) if isinstance(res, dict) else (res or [])
    except: return []

# --- LOGIN ---
if not st.session_state.registado:
    st.title("🎤 FF Karaoke")
    nome = st.text_input("Como quer ser chamado?")
    if st.button("Entrar"):
        if nome: st.session_state.nome = nome; st.session_state.registado = True; st.rerun()
else:
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
        pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}").json() or {}
    except: status = {}; pedidos = {}

    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()

    # Verifica se o cantor já tem pedidos na fila
    ja_na_fila = any(p.get("cantor", "").strip().lower() == meu_nome for p in (pedidos.values() if pedidos else []))

    # 1. É a vez do cliente
    if nome_firebase == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()

    # 2. Música a tocar
    elif nome_firebase == meu_nome and status.get("comando") == "play":
        st.info("🎤 A sua música está a tocar na TV!")

    # 3. Pesquisa e Playlist
    else:
        if ja_na_fila:
            st.warning("⚠️ Você já tem pedidos na fila. Aguarde a sua vez!")
        else:
            st.info("Prepare a sua playlist e envie para o DJ!")
        
        # Gestão da Playlist
        st.subheader("Playlist (Máx 5)")
        if len(st.session_state.minha_playlist) > 0:
            for i, m in enumerate(st.session_state.minha_playlist):
                col1, col2 = st.columns([4, 1])
                col1.write(f"{i+1}. {m}")
                if not ja_na_fila and col2.button("❌", key=f"rem_{i}"):
                    st.session_state.minha_playlist.pop(i)
                    st.rerun()
        else:
            st.write("Sua playlist está vazia.")
        
        # Adicionar nova música (apenas se não estiver na fila)
        if not ja_na_fila and len(st.session_state.minha_playlist) < 5:
            st.divider()
            termo = st.text_input("🔍 Pesquisar música:")
            catalogo = obter_catalogo()
            resultados = [m for m in catalogo if termo.lower() in str(m).lower()] if termo else []
            
            if termo and resultados:
                musica_sel = st.selectbox("Escolha na lista:", resultados)
                if st.button("➕ Adicionar à Playlist"):
                    st.session_state.minha_playlist.append(musica_sel)
                    st.rerun()
        elif not ja_na_fila:
            st.warning("Playlist cheia! (Máximo 5 músicas)")

        # Enviar pedido (apenas se não estiver na fila)
        if not ja_na_fila and st.session_state.minha_playlist:
            if st.button("🚀 Enviar Pedidos para o DJ", use_container_width=True):
                for m in st.session_state.minha_playlist:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": m})
                st.session_state.minha_playlist = [] 
                st.success("Pedidos enviados! Aguarde a sua vez.")
                st.balloons()
                time.sleep(2); st.rerun()

    st.divider()
    if st.button("Sair"): st.session_state.registado = False; st.rerun()
    
    time.sleep(3); st.rerun()
