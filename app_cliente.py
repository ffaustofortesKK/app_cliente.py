import streamlit as st
import requests

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

# Captura o prestador da URL
query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_FIREBASE_PEDIDOS = f"{BASE_URL}/pedidos_{prestador_slug}.json"
URL_STATUS = f"{BASE_URL}/status_{prestador_slug}.json"
URL_CATALOGO = f"{BASE_URL}/catalogo.json"

if 'registado' not in st.session_state: st.session_state.registado = False

@st.cache_data(ttl=60)
def obter_catalogo():
    try:
        res = requests.get(URL_CATALOGO).json()
        return list(res.values()) if isinstance(res, dict) else (res or [])
    except: return ["Erro ao carregar catálogo"]

# --- LOGIN ---
if not st.session_state.registado:
    st.title("🎤 FF Karaoke")
    nome = st.text_input("Como quer ser chamado no palco?")
    if st.button("Entrar"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    # --- INTERFACE PRINCIPAL ---
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # Verifica o estado atual na TV
    status = requests.get(URL_STATUS).json() or {}
    
    # 1. Lógica do botão de Play (se for a vez do cliente)
    if status.get("cantor") == st.session_state.nome and status.get("comando") == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.info("A música começou na TV. Solte a voz!")
    
    # 2. Se a música está a tocar
    elif status.get("cantor") == st.session_state.nome and status.get("comando") == "play":
        st.info("🎤 A sua música está a tocar na TV!")
    
    # 3. Se não é a vez dele, mostra a lista de músicas
    else:
        catalogo = obter_catalogo()
        termo_busca = st.text_input("🔍 Pesquise a sua música:")
        
        musica_escolhida = None
        if termo_busca:
            resultados = [m for m in catalogo if termo_busca.lower() in str(m).lower()]
            if resultados:
                musica_escolhida = st.selectbox("Selecione:", resultados)
            else:
                st.warning("Nenhuma música encontrada.")
        
        if musica_escolhida and st.button("🎤 Confirmar Pedido"):
            payload = {"cantor": st.session_state.nome, "musica": musica_escolhida}
            requests.post(URL_FIREBASE_PEDIDOS, json=payload)
            st.success(f"Pedido enviado: {musica_escolhida}!")
            st.balloons()

    st.divider()
    if st.button("Sair"): 
        st.session_state.registado = False
        st.rerun()

    # Atualiza a página a cada 5 segundos para verificar se é a vez do cliente
    time.sleep(5)
    st.rerun()
