import streamlit as st
import requests
import time

# --- CONFIGURAÇÃO E URL ---
# Captura o parâmetro '?prestador=...' da URL do navegador
params = st.query_params
prestador_alvo = params.get("prestador")

if not prestador_alvo:
    st.error("Erro: Link inválido. Por favor, utilize o QR Code do prestador.")
    st.stop()

# URL para salvar pedidos na "pasta" específica deste prestador no Firebase
URL_FIREBASE_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_alvo}.json"
URL_FIREBASE_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

st.set_page_config(page_title=f"Karaoke - {prestador_alvo.upper()}", layout="centered")

# CSS para o visual do Cliente
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; color: white; }
    </style>
""", unsafe_allow_html=True)

# Registro do Cliente na sessão
if 'registado' not in st.session_state: 
    st.session_state.registado = False

if not st.session_state.registado:
    st.subheader("📝 Identifique-se")
    nome = st.text_input("Qual o seu nome?")
    if st.button("Entrar no Karaoke"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    # 1. BUSCA NO CATÁLOGO
    busca = st.text_input("🔍 Pesquisar música:")
    escolha = None
    
    if busca:
        try:
            resp = requests.get(URL_FIREBASE_CATALOGO, timeout=5)
            dados = resp.json()
            cat = list(dados.keys()) if isinstance(dados, dict) else dados
            resultados = [m for m in cat if busca.lower() in m.lower()]
            escolha = st.selectbox("Selecione a sua música:", resultados)
        except:
            st.error("Erro ao carregar catálogo.")

    # 2. CONFIRMAR PEDIDO
    if escolha:
        if st.button("Confirmar Pedido"):
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": escolha})
            st.balloons()
            st.success("Pedido enviado!")
            time.sleep(2)
            st.rerun()

    # 3. PEDIDO MANUAL
    st.divider()
    st.subheader("Não encontrou?")
    pedido_manual = st.text_input("Digite o nome da música:")
    if st.button("Enviar Pedido Manual"):
        if pedido_manual:
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": pedido_manual, "status": "manual"})
            st.success("Pedido manual enviado!")
            time.sleep(2)
            st.rerun()
