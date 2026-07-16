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

if not st.session_state.registado:
    st.title("🎤 FF Karaoke")
    nome = st.text_input("Como quer ser chamado?")
    if st.button("Entrar"):
        if nome: st.session_state.nome = nome; st.session_state.registado = True; st.rerun()
else:
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
    except: status = {}

    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()

    if nome_firebase == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
    elif nome_firebase == meu_nome and status.get("comando") == "play":
        st.info("🎤 A sua música está a tocar na TV!")
    else:
        # AQUI COMEÇA A NOVA LÓGICA DE PEDIDOS
        st.info("Aguarde a sua vez e prepare a sua playlist!")
        
        # Gestão da Playlist
        st.subheader("Minha Playlist (Máx 5)")
        for i, m in enumerate(st.session_state.minha_playlist):
            col1, col2 = st.columns([4, 1])
            col1.write(f"{i+1}. {m}")
            if col2.button("❌", key=f"rem_{i}"):
                st.session_state.minha_playlist.pop(i); st.rerun()
        
        if len(st.session_state.minha_playlist) < 5:
            termo = st.text_input("🔍 Pesquisar música no catálogo:")
            resultados = [m for m in obter_catalogo() if termo.lower() in str(m).lower()] if termo else []
            if termo and resultados:
                musica_sel = st.selectbox("Escolha:", resultados)
                if st.button("➕ Adicionar à Playlist"):
                    st.session_state.minha_playlist.append(musica_sel); st.rerun()
        
        st.divider()
        st.subheader("📝 Pedido Personalizado")
        pedido_extra = st.text_area("Não encontrou? Escreva o nome da música:")
        
        # Lógica de Envio Único (Bloqueia se não for a vez ou se não tiver nada)
        if st.button("🚀 Enviar Pedidos para o DJ"):
            if not st.session_state.minha_playlist and not pedido_extra:
                st.warning("Adicione músicas à playlist ou escreva um pedido.")
            else:
                # Enviar Playlist
                for m in st.session_state.minha_playlist:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": m})
                # Enviar Pedido Extra
                if pedido_extra:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": f"PEDIDO: {pedido_extra}"})
                
                st.session_state.minha_playlist = []
                st.warning("⚠️ O seu pedido foi enviado, mas nem todas as músicas estão disponíveis em karaoke. Aguarde pela sua vez.")
                time.sleep(4); st.rerun()

    if st.button("Sair"): st.session_state.registado = False; st.rerun()
    time.sleep(3); st.rerun()
