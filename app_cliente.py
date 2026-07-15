import streamlit as st
import requests

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

# Captura o prestador da URL
query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")
URL_FIREBASE_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"
URL_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

if 'registado' not in st.session_state: 
    st.session_state.registado = False

# Função para buscar catálogo com cache (otimiza a velocidade)
@st.cache_data(ttl=600)
def obter_catalogo():
    try:
        res = requests.get(URL_CATALOGO).json()
        # Se for um dicionário (importação do Firebase), transforma em lista
        if isinstance(res, dict):
            return list(res.values())
        return res if res else []
    except:
        return ["Erro ao carregar catálogo"]

if not st.session_state.registado:
    nome = st.text_input("Seu nome:")
    if st.button("Entrar"):
        if nome:
            st.session_state.nome = nome
            st.session_state.registado = True
            st.rerun()
else:
    st.title(f"Bem-vindo, {st.session_state.nome}!")
    
    catalogo = obter_catalogo()
    
    # BARRA DE PESQUISA INTELIGENTE
    termo_busca = st.text_input("🔍 Pesquise sua música aqui:")
    
    musica_escolhida = None
    if termo_busca:
        # Filtra a lista baseada no que o cliente digita
        resultados = [m for m in catalogo if termo_busca.lower() in str(m).lower()]
        if resultados:
            musica_escolhida = st.selectbox("Selecione sua música:", resultados)
        else:
            st.warning("Nenhuma música encontrada com esse nome.")
    
    # Confirmar Pedido
    if musica_escolhida and st.button("🎤 Confirmar Pedido"):
        payload = {"cantor": st.session_state.nome, "musica": musica_escolhida}
        requests.post(URL_FIREBASE_PEDIDOS, json=payload)
        st.success(f"Pedido enviado: {musica_escolhida}!")
        st.balloons() # Efeito visual bacana

    st.divider()
    if st.button("Sair"): 
        st.session_state.registado = False
        st.rerun()
