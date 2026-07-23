import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

if 'registado' not in st.session_state: st.session_state.registado = False

query_params = st.query_params
prestador_slug = query_params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{prestador_slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{prestador_slug}.json"
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
    try:
        status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=2).json() or {}
        pedidos_json = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=2).json() or {}
    except: 
        status = {}
        pedidos_json = {}

    nome_firebase = str(status.get("cantor", "")).strip().lower()
    meu_nome = str(st.session_state.nome).strip().lower()
    
    fila = list(pedidos_json.items()) if pedidos_json else []
    posicao = next((i for i, (p_id, p) in enumerate(fila) if str(p.get('cantor')).strip().lower() == meu_nome), -1)

    tem_pedido_na_fila = posicao != -1
    esta_a_cantar_ou_chamado = (nome_firebase == meu_nome)
    comando_atual = status.get("comando")

    if esta_a_cantar_ou_chamado:
        if comando_atual == "aguardando_play":
            st.success("🎉 É a tua vez! Prepara-te, o vídeo vai começar a tocar na tela...")
        elif comando_atual == "play":
            st.info("🎵 A tua música está a passar na tela!")
    elif tem_pedido_na_fila:
        st.warning("⚠️ O seu pedido foi enviado. Aguarde a sua vez.")
        if posicao == 0:
            st.info("📢 Estás quase lá, aguarde o sinal para começar.")
        else:
            st.write(f"🔢 Existem **{posicao}** músicas à sua frente.")
    else:
        st.success("✅ Já podes enviar a tua próxima música!")

    st.divider()
    st.subheader("🔍 Pesquisar Música no Catálogo")
    
    termo = st.text_input("Digite o nome do artista ou música:")
    resultados = [m for m in obter_catalogo() if termo.lower() in str(m).lower()] if termo else []
    
    musica_escolhida = None
    if termo and resultados:
        musica_escolhida = st.selectbox("Escolha na lista:", resultados, key="select_busca_musica")
        if st.button("🚀 Enviar para o DJ", key="btn_enviar_catalogo", use_container_width=True):
            if tem_pedido_na_fila or esta_a_cantar_ou_chamado:
                st.error("⛔ Só podes enviar outra música assim que a tua atuação atual terminar!")
            elif not musica_escolhida:
                st.warning("Selecione uma música do catálogo.")
            else:
                requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": musica_escolhida})
                st.success("Pedido enviado com sucesso!")
                time.sleep(1)
                st.rerun()

    st.divider()
    st.subheader("📝 Ou Pedido Personalizado")
    pedido_extra = st.text_area("Não encontrou no catálogo? Escreva aqui:", key="input_pedido_extra")
    
    if st.button("🚀 Enviar Pedido Personalizado para o DJ", key="btn_enviar_personalizado", use_container_width=True):
        if tem_pedido_na_fila or esta_a_cantar_ou_chamado:
            st.error("⛔ Só podes enviar outra música assim que a tua atuação atual terminar!")
        elif not pedido_extra:
            st.warning("Escreva o seu pedido personalizado.")
        else:
            requests.post(URL_PEDIDOS, json={"cantor": st.session_state.nome, "musica": f"PEDIDO: {pedido_extra}"})
            st.success("Pedido enviado com sucesso!")
            time.sleep(1)
            st.rerun()

    st.divider()
    if st.button("Sair"): 
        st.session_state.registado = False
        st.rerun()
    
    time.sleep(1.5)
    st.rerun()
