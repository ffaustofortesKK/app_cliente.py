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
        if nome: 
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    # Buscar Estado e Pedidos
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
        pedidos_json = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}").json() or {}
    except: 
        status = {}
        pedidos_json = {}

    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    
    # Verificar se o utilizador já tem pedido na fila
    fila = list(pedidos_json.items()) if pedidos_json else []
    posicao = next((i for i, (p_id, p) in enumerate(fila) if str(p.get('cantor')).strip().lower() == meu_nome), -1)

    # 1. VEZ DO CANTOR
    if nome_firebase == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 Próximo és tu, preparado?")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
            
    # 2. ESPERANDO NA FILA
    elif posicao != -1:
        st.warning("⚠️ O seu pedido foi enviado. Aguarde a sua vez.")
        if posicao == 0:
            st.info("📢 Estás quase lá, aguarde o sinal para começar.")
        else:
            st.write(f"🔢 Existem **{posicao}** músicas à sua frente.")
            
    # 3. ESTADO NORMAL
    else:
        st.info("Prepare a sua playlist!")
        
        # 1. PLAYLIST ATUAL (MÁX 3)
        st.subheader("Minha Playlist (Máx 3)")
        for i, m in enumerate(st.session_state.minha_playlist):
            col1, col2 = st.columns([4, 1])
            col1.write(f"{i+1}. {m}")
            if col2.button("❌", key=f"rem_{i}"):
                st.session_state.minha_playlist.pop(i)
                st.rerun()
        
        st.divider()
        
        # 2. PESQUISA (Agora sempre disponível, mesmo com 3 músicas)
        st.subheader("🔍 Pesquisa e Adição")
        termo = st.text_input("Pesquisar nova música:")
        resultados = [m for m in obter_catalogo() if termo.lower() in str(m).lower()] if termo else []
        
        if termo and resultados:
            musica_sel = st.selectbox("Escolha:", resultados, key="select_pesquisa_musica")
            if st.button("➕ Adicionar à Playlist"):
                if len(st.session_state.minha_playlist) >= 3:
                    st.warning("⚠️ A sua playlist já atingiu o limite de 3 músicas! Remova uma das músicas existentes na sua playlist para poder adicionar esta nova.")
                else:
                    st.session_state.minha_playlist.append(musica_sel)
                    st.success("Música adicionada com sucesso!")
                    st.rerun()
        
        st.divider()
        st.subheader("📝 Pedido Personalizado")
        pedido_extra = st.text_area("Não encontrou?", key="input_pedido_extra")
        
        # LÓGICA DE ENVIO PARA O DJ COM BOTÃO LIMPAR
        col_envio, col_limpar = st.columns(2)
        with col_envio:
            btn_enviar = st.button("🚀 Enviar próxima música para o DJ", use_container_width=True)
        with col_limpar:
            btn_limpar = st.button("🧹 Limpar", use_container_width=True)

        if btn_limpar:
            st.session_state.minha_playlist = []
            st.rerun()

        if btn_enviar:
            if not st.session_state.minha_playlist and not pedido_extra:
                st.warning("Adicione músicas à playlist.")
            else:
                if st.session_state.minha_playlist:
                    musica_envio = st.session_state.minha_playlist.pop(0)
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": musica_envio})
                elif pedido_extra:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": f"PEDIDO: {pedido_extra}"})
                
                st.rerun()

    st.divider()
    if st.button("Sair"): 
        st.session_state.registado = False
        st.rerun()
    
    time.sleep(3)
    st.rerun()
