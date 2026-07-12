import streamlit as st
import requests
import time

# --- CONFIGURAÇÃO E URL ---
# Captura o parâmetro '?prestador=...'
params = st.query_params
prestador_alvo = params.get("prestador")

if not prestador_alvo:
    st.error("Erro: Link inválido. Por favor, utilize o QR Code do prestador.")
    st.stop()

URL_FIREBASE_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_alvo}.json"
URL_FIREBASE_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

st.set_page_config(page_title="FF Karaoke Cloud", layout="centered")

# CSS para o visual do Cliente (Dark Mode)
st.markdown("""
    <style>
    .stApp { background-color: #0e0e0e; }
    h1, h2, h3, p, label, div { color: #ffffff !important; }
    .big-box { background-color: #1a1a1a; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# Registro do Cliente
if 'registado' not in st.session_state: 
    st.session_state.registado = False

if not st.session_state.registado:
    st.title("🎤 Bem-vindo!")
    st.subheader("📝 Identifique-se para começar")
    nome = st.text_input("Qual o seu nome?")
    if st.button("Entrar no Karaoke"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    st.markdown('<div class="big-box">', unsafe_allow_html=True)
    # 1. BUSCA NO CATÁLOGO
    st.subheader("🔍 Pesquisar música")
    busca = st.text_input("Digite o nome da música:")
    escolha = None
    
    if busca:
        try:
            resp = requests.get(URL_FIREBASE_CATALOGO, timeout=5)
            dados = resp.json()
            cat = list(dados.keys()) if isinstance(dados, dict) else dados
            resultados = [m for m in cat if busca.lower() in m.lower()]
            if resultados:
                escolha = st.selectbox("Selecione a sua música:", resultados)
            else:
                st.write("Nenhuma música encontrada no catálogo.")
        except:
            st.error("Erro ao conectar com o catálogo.")

    # 2. CONFIRMAR PEDIDO
    if escolha:
        if st.button("Confirmar Pedido"):
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": escolha})
            st.balloons()
            st.success(f"Pedido enviado: {escolha}")
            time.sleep(2)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. PEDIDO MANUAL
    st.markdown('<br><div class="big-box">', unsafe_allow_html=True)
    st.subheader("Não encontrou?")
    pedido_manual = st.text_input("Digite o nome da música (Manual):")
    if st.button("Enviar Pedido Manual"):
        if pedido_manual:
            requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": pedido_manual, "status": "manual"})
            st.success("Pedido manual enviado!")
            time.sleep(2)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
