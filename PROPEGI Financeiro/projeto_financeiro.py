import streamlit as st

st.set_page_config(page_title="PROPEGI Financeiro", page_icon="../../images/upeLogo.png", layout="wide", initial_sidebar_state="collapsed")
st.title("Home")
st.write("Use os links abaixo para navegar:")

st.page_link("projeto_financeiro.py", label="Home", icon="🏠")
st.page_link("pages/01_analise1_comparativa.py", label="Análise 1 — Comparativo (Heatmap)", icon="1️⃣")
st.page_link("pages/02_analise2_somatorio.py", label="Análise 2 — Somatório por Projeto", icon="2️⃣")
st.page_link("pages/03_analise3_total_mensal.py", label="Análise 3 — Total Mensal", icon="3️⃣")