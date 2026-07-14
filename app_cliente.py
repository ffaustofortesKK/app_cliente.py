import streamlit as st
import requests
import time

# --- CONFIGURAÇÕES ---
URL_BASE_FIREBASE = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
LINK_LOGO = "https://cdn.phototourl.com/free/2026-07-03-793a0f18-6143-44c8-b56e-e44af828c30c.png"
URL_SOM_PALMAS = "https://www.soundjay.com/misc/sounds/applause-2.mp3"

st.set_page_config(page_title="FF KARAOKE CLOUD", layout="wide")

# CSS (Mantido o seu estilo)
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(rgba(9, 10, 15, 0.85), rgba(9, 10, 15, 0.85)), url('{LINK_LOGO}');
        background-size: contain; background-repeat: no-repeat; background-position: center; color: white; }}
    </style>
""", unsafe_allow_html=True)

# 1. PEGAR O PRESTADOR DA URL
query_params = st.query_params
prestador_slug = query_params.get("prestador")

if not prestador_slug:
    st.error("❌ Acesso inválido! Por favor, use o link fornecido pelo prestador.")
    st.stop()

# URL dinâmica baseada no prestador
URL_PEDIDOS_ESPECIFICO = f"{URL_BASE_FIREBASE}/pedidos_{prestador_slug}.json"
URL_CATALOGO = f"{URL_BASE_FIREBASE}/catalogo.json"

# --- LOGIN SIMPLES ---
if 'registado' not in st.session_state: st.session_state.registado = False

if not st.session_state.registado:
    st.subheader("📝 Registo Inicial")
    nome = st.text_input("Qual o seu nome?")
    if st.button("Concluir Registo"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # BUSCA
    busca = st.text_input("🔍 Pesquisar Música:")
    escolha = None
    if busca:
        try:
            resp = requests.get(URL_CATALOGO, timeout=5)
            dados = resp.json()
            cat = list(dados.keys()) if isinstance(dados, dict) else dados
            resultados = [m for m in cat if busca.lower() in m.lower()]
            escolha = st.selectbox("Selecione a música:", resultados)
        except: st.error("Erro ao carregar catálogo.")

    # --- ENVIO ---
    if escolha and st.button("Confirmar Pedido"):
        payload = {"cantor": st.session_state.nome, "musica": escolha}
        requests.post(URL_PEDIDOS_ESPECIFICO, json=payload)
        st.balloons()
        st.success("Enviado com sucesso!")
        st.audio(URL_SOM_PALMAS, autoplay=True)
        time.sleep(2)
        st.rerun()

    st.divider()
    
    # MANUAL
    pedido_manual = st.text_input("Não achou? Digite o nome:")
    if st.button("Confirmar Pedido Manual"):
        if pedido_manual:
            payload = {"cantor": st.session_state.nome, "musica": pedido_manual, "status": "manual"}
            requests.post(URL_PEDIDOS_ESPECIFICO, json=payload)
            st.success("Pedido manual enviado!")
            time.sleep(2)
            st.rerun()
