import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

if 'registado' not in st.session_state: st.session_state.registado = False
if 'minha_playlist' not in st.session_state: st.session_state.minha_playlist = []

query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")

# URLs ajustadas em perfeita sintonia com o painel central do DJ e o sistema global
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{prestador_slug}.json"
URL_PEDIDOS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"
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
    # Buscar Estado e Pedidos em tempo real
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
        pedidos_json = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}").json() or {}
    except: 
        status = {}
        pedidos_json = {}

    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    
    # Verificar se o utilizador já tem pedido na fila global
    fila = list(pedidos_json.items()) if pedidos_json else []
    posicao = next((i for i, (p_id, p) in enumerate(fila) if str(p.get('cantor')).strip().lower() == meu_nome), -1)

    # 1. VEZ DO CANTOR
    if nome_firebase == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 Próximo és tu, preparado?")
        musica_atual_vez = status.get("musica", "Música de Karaoke")
        
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            # Envia o comando de play e passa explicitamente os dados para o leitor abrir
            requests.patch(URL_STATUS, json={
                "comando": "play",
                "musica": musica_atual_vez
            })
            st.rerun()
            
    # 2. ESPERANDO NA FILA
    elif posicao != -1:
        st.warning("⚠️ O seu pedido foi enviado. Aguarde a sua vez.")
        if posicao == 0:
            st.info("📢 Estás quase lá, aguarde o sinal para começar.")
        else:
            st.write(f"🔢 Existem **{posicao}** músicas à sua frente.")
            
    # 3. ESTADO NORMAL (ADICIONAR À PLAYLIST)
    else:
        st.info("Prepare a sua playlist!")
        
        # Playlist atual (Máx 3)
        st.subheader("Minha Playlist (Máx 3)")
        for i, m in enumerate(st.session_state.minha_playlist):
            col1, col2 = st.columns([4, 1])
            col1.write(f"{i+1}. {m}")
            if col2.button("❌", key=f"rem_{i}"):
                st.session_state.minha_playlist.pop(i)
                st.rerun()
        
        # Pesquisa de músicas no catálogo
        if len(st.session_state.minha_playlist) < 3:
            termo = st.text_input("🔍 Pesquisar música:")
            resultados = [m for m in obter_catalogo() if termo.lower() in str(m).lower()] if termo else []
            if termo and resultados:
                musica_sel = st.selectbox("Escolha:", resultados)
                if st.button("➕ Adicionar à Playlist"):
                    st.session_state.minha_playlist.append(musica_sel)
                    st.rerun()
        
        st.divider()
        st.subheader("📝 Pedido Personalizado")
        pedido_extra = st.text_area("Não encontrou?")
        
        # Lógica de envio para a fila global do DJ
        if st.button("🚀 Enviar próxima música para o DJ", use_container_width=True):
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
