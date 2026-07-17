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
        return list(res) if isinstance(res, list) else (list(res.values()) if isinstance(res, dict) else [])
    except: return []

if not st.session_state.registado:
    st.title("🎤 FF Karaoke")
    nome = st.text_input("Como quer ser chamado?")
    if st.button("Entrar"):
        if nome: st.session_state.nome = nome; st.session_state.registado = True; st.rerun()
else:
    # --- LÓGICA DE STATUS ---
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    except: status = {}

    # Comparação segura e normalizada
    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    comando = status.get("comando", "")

    # Interface de Controlo
    if nome_firebase == meu_nome and comando == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
    elif nome_firebase == meu_nome and comando == "play":
        st.info("🎤 A sua música está a tocar na TV!")
    else:
        st.info("Aguarde a sua vez e prepare a sua playlist!")
        
        # 1. PLAYLIST ATUAL
        if st.session_state.minha_playlist:
            st.subheader("Minha Playlist")
            for i, m in enumerate(st.session_state.minha_playlist):
                col1, col2 = st.columns([4, 1])
                col1.write(f"{i+1}. {m}")
                if col2.button("❌", key=f"rem_{i}"):
                    st.session_state.minha_playlist.pop(i); st.rerun()
        
        # 2. PESQUISA
        if len(st.session_state.minha_playlist) < 5:
            termo = st.text_input("🔍 Pesquisar música no catálogo:")
            if termo:
                resultados = [m for m in obter_catalogo() if termo.lower() in str(m).lower()]
                if resultados:
                    musica_sel = st.selectbox("Escolha uma opção:", resultados)
                    if st.button("➕ Adicionar à Playlist"):
                        st.session_state.minha_playlist.append(musica_sel); st.rerun()
        
        # 3. PEDIDO MANUAL
        st.divider()
        st.subheader("📝 Pedido Personalizado")
        pedido_extra = st.text_area("Não encontrou? Escreva o nome da música:")
        
        # 4. BOTÃO DE ENVIO
        if st.button("🚀 Enviar Pedidos para o DJ", use_container_width=True):
            if not st.session_state.minha_playlist and not pedido_extra:
                st.warning("Adicione músicas à playlist ou escreva um pedido.")
            else:
                for m in st.session_state.minha_playlist:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": m})
                if pedido_extra:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": f"PEDIDO: {pedido_extra}"})
                
                st.session_state.minha_playlist = []
                st.success("⚠️ Pedido enviado! Aguarde a sua vez.")
                time.sleep(2); st.rerun()

    st.divider()
    if st.button("Sair"): st.session_state.registado = False; st.rerun()
    
    # Refresh automático rápido para o botão aparecer assim que o DJ acionar
    time.sleep(2); st.rerun()
