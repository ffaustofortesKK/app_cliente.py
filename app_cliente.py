import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - CLIENTE", layout="centered")

query_params = st.query_params
prestador_slug = query_params.get("prestador")

if not prestador_slug:
    st.error("Prestador não encontrado na URL.")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{prestador_slug}.json"

if 'registado' not in st.session_state: st.session_state.registado = False

if not st.session_state.registado:
    nome = st.text_input("Como quer ser chamado?")
    if st.button("Entrar"): st.session_state.nome = nome; st.session_state.registado = True; st.rerun()
else:
    status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
    meu_nome = str(st.session_state.nome).strip().lower()
    cantor_firebase = str(status.get("cantor", "")).strip().lower()

    if cantor_firebase == meu_nome and status.get("comando") == "aguardando_play":
        st.success("🎉 É a sua vez!")
        if st.button("▶️ COMEÇAR A MINHA MÚSICA"):
            requests.patch(URL_STATUS, json={"comando": "play"})
            st.rerun()
    elif cantor_firebase == meu_nome and status.get("comando") == "play":
        st.info("🎤 Música a tocar na TV!")
    else:
        st.write("Aguarde a sua vez...")
    time.sleep(2); st.rerun()
