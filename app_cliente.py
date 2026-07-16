import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{prestador_slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"
URL_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

if 'registado' not in st.session_state: st.session_state.registado = False

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
    # Busca forçada sem cache do status atual
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
    except: status = {}

    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    
    # Exibe o botão de Play se o sistema estiver aguardando
    if nome_firebase == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
            
    elif nome_firebase == meu_nome and status.get("comando") == "play":
        st.info("🎤 A sua música está a tocar na TV!")
        
    else:
        st.subheader("🔍 Pesquisar Música")
        termo = st.text_input("Digite o nome da música:", placeholder="🔍 Pesquisar...")
        
        catalogo = obter_catalogo()
        resultados = [m for m in catalogo if termo.lower() in str(m).lower()] if termo else []
        
        if termo and resultados:
            musica_selecionada = st.selectbox("Escolha na lista:", resultados)
            if st.button("🎤 Confirmar Pedido"):
                requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": musica_selecionada})
                st.success(f"Pedido enviado!")
                st.balloons()
        elif termo:
            st.warning("Nenhuma música encontrada.")

    st.divider()
    if st.button("Sair"): st.session_state.registado = False; st.rerun()
    
    time.sleep(3); st.rerun()
