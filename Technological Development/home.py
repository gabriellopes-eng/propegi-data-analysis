import streamlit as st

st.set_page_config(page_title="Projeto de Desenvolvimento Tecnológico", layout="wide",initial_sidebar_state="collapsed") #->collapsed serve para esconder a sidebar

st.title("Home")
st.write("Use os links abaixo para navegar:")

st.page_link("home.py", label="Home", icon="🏠")
st.page_link("pages/01_recebimentos_mensais.py", label="Recebimentos mensais — Agência / Unidade / IA-UPE", icon="📅")
st.page_link("pages/02_projetos_por_segmento.py", label="Projetos em desenvolvimento por segmento/ano", icon="📊")
st.page_link("pages/03_recebimentos_anuais.py", label="Recebimentos anuais por órgão", icon="📈")
st.page_link("pages/04_recebimentos_por_setor.py", label="Recebimentos por setor (segmento)", icon="🥧")

