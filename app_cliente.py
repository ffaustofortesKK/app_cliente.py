import streamlit as st
import requests
import time

st.set_page_config(page_title="FF Karaoke", layout="wide")

# 1. CAPTURAR O PRESTADOR DA URL
query_params = st.query_params
prestador_slug = query_params.get("prestador")

if not prestador_slug:
    st.error("❌ Link inválido. Por favor, use o QR Code do seu prestador.")
    st.stop()

# 2. DEFINIR O DESTINO DO PEDIDO (Dinâmico)
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"
URL_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"

# ... (Mantenha o seu CSS e a lógica de login do cantor) ...

# 3. NO MOMENTO DO ENVIO (Onde você faz o POST)
if st.button("Confirmar Pedido"):
    # O pedido vai cair EXATAMENTE na lista do prestador que está no link
    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": escolha})
    st.balloons()
    st.success("Pedido enviado para o seu prestador!")
    time.sleep(2)
    st.rerun()
