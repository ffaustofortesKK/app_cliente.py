import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

if 'registado' not in st.session_state: st.session_state.registado = False
if 'minha_playlist' not in st.session_state: st.session_state.minha_playlist = []

slug = st.query_params.get("prestador", "geral")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Estilo para o piscar
st.markdown("""
    <style>
        .blink { animation: blinker 1s linear infinite; color: #FF4B4B; font-weight: bold; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

if not st.session_state.registado:
    nome = st.text_input("Como quer ser chamado?")
    if st.button("Entrar"):
        if nome: st.session_state.nome = nome; st.session_state.registado = True; st.rerun()
else:
    meu_nome = str(st.session_state.nome).strip().lower()
    
    # Busca dados
    status = requests.get(f"{URL_STATUS}?t={time.time()}").json() or {}
    pedidos = requests.get(f"{URL_PEDIDOS}?t={time.time()}").json() or {}
    
    # Verifica se tem pedido na fila
    meu_pedido_na_fila = next((p for p in pedidos.values() if str(p.get('cantor')).strip().lower() == meu_nome), None)
    
    # 1. ESTADO: VEZ DO CANTOR
    if str(status.get("cantor", "")).strip().lower() == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 É a sua vez de brilhar!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA", use_container_width=True):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
            
    # 2. ESTADO: PEDIDO PENDENTE NA FILA
    elif meu_pedido_na_fila:
        lista_ids = list(pedidos.keys())
        posicao = lista_ids.index(next(k for k,v in pedidos.items() if str(v.get('cantor')).strip().lower() == meu_nome))
        
        st.info("⚠️ Pedido enviado! Aguarde a sua vez.")
        if posicao == 0:
            st.markdown('<p class="blink">📢 A seguir és o próximo!</p>', unsafe_allow_html=True)
        else:
            st.write(f"Existem **{posicao}** músicas à tua frente.")
            
    # 3. ESTADO: PODE PEDIR
    else:
        st.subheader("Nova Música")
        termo = st.text_input("Pesquisar:")
        if termo:
            # (Adicione aqui sua lógica de catálogo)
            if st.button("Adicionar"): st.session_state.minha_playlist.append(termo); st.rerun()
        
        if st.session_state.minha_playlist:
            if st.button("🚀 Enviar Pedidos"):
                for m in st.session_state.minha_playlist:
                    requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": m})
                st.session_state.minha_playlist = []
                st.rerun()

    if st.button("Sair"): st.session_state.registado = False; st.rerun()
    time.sleep(3); st.rerun()
