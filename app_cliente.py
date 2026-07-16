import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

# Captura o prestador da URL
query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")

# URLs
BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_FIREBASE_PEDIDOS = f"{BASE_URL}/pedidos_{prestador_slug}.json"
URL_STATUS = f"{BASE_URL}/status_{prestador_slug}.json"
URL_CATALOGO = f"{BASE_URL}/catalogo.json"

if 'registado' not in st.session_state: 
    st.session_state.registado = False

@st.cache_data(ttl=600)
def obter_catalogo():
    try:
        res = requests.get(URL_CATALOGO).json()
        return list(res.values()) if isinstance(res, dict) else (res or [])
    except:
        return ["Erro ao carregar catálogo"]

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
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # Busca de status com anti-cache
    try:
        url_status_cache = f"{URL_STATUS}?nocache={time.time()}"
        status = requests.get(url_status_cache).json() or {}
    except:
        status = {}

    # --- LÓGICA DE COMPARAÇÃO ROBUSTA ---
    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    comando_atual = status.get("comando", "")

    # Debug Visual (SE NÃO APARECER O BOTÃO, OLHE PARA ESTES DADOS)
    with st.expander("Ver Estado do Sistema (Debug)"):
        st.write(f"Firebase: '{nome_firebase}'")
        st.write(f"Sua Sessão: '{meu_nome}'")
        st.write(f"Comando: '{comando_atual}'")

    # 1. Lógica do botão de Play
    if nome_firebase == meu_nome and comando_atual == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.info("A música começou na TV. Solte a voz!")
            st.rerun()
    
    # 2. Se a música está a tocar
    elif nome_firebase == meu_nome and comando_atual == "play":
        st.info("🎤 A sua música está a tocar na TV! Divirta-se!")
    
    # 3. Lista de pedidos
    else:
        st.write("Aguardando a sua vez...")
        catalogo = obter_catalogo()
        termo_busca = st.text_input("🔍 Pesquise sua música aqui:")
        
        musica_escolhida = None
        if termo_busca:
            resultados = [m for m in catalogo if termo_busca.lower() in str(m).lower()]
            if resultados:
                musica_escolhida = st.selectbox("Selecione sua música:", resultados)
        
        if musica_escolhida and st.button("🎤 Confirmar Pedido"):
            payload = {"cantor": st.session_state.nome, "musica": musica_escolhida}
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": musica_escolhida})
            st.success(f"Pedido enviado: {musica_escolhida}!")
            st.balloons()

    st.divider()
    if st.button("Sair"): 
        st.session_state.registado = False
        st.rerun()

    time.sleep(5)
    st.rerun()
