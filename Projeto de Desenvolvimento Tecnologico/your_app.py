import streamlit as st

st.set_page_config(page_title="Projeto de Desenvolvimento Tecnológico", layout="wide",initial_sidebar_state="collapsed") #->collapsed serve para esconder a sidebar

st.title("Home")
st.write("Use os links abaixo para navegar:")

st.page_link("your_app.py", label="Home", icon="🏠")
st.page_link("pages/page_1.py", label="Análise 1 — Mensal", icon="1️⃣")
st.page_link("pages/page_2.py", label="Análise 2 — Exemplo", icon="2️⃣")
st.page_link("pages/page_3.py", label="Análise 3 — Exemplo", icon="3️⃣")
st.page_link("pages/page_4.py", label="Análise 4 — Exemplo ", icon="4️⃣")


