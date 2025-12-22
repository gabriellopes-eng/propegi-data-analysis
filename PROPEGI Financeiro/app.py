import streamlit as st
import os

st.set_page_config(page_title="PROPEGI Financeiro", page_icon="../images/upeLogo.png", layout="wide")

# Título principal
st.title("PROPEGI Financeiro")

# Logo centralizado na barra lateral
with st.sidebar:
    col1, col2, col3 = st.columns([1, 3, 1])
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'upeLogo.png')
    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        else:
            st.warning("Logo da UPE não encontrado em images/upeLogo.png")

# Navegação moderna entre páginas
analise1 = st.Page(
    page="pages/01_heatmap_comparativo.py",
    title="Heatmap Comparativo",
    icon="🌡️",
    default=True,
)

analise2 = st.Page(
    page="pages/02_somatorio_projetos.py",
    title="Somatório de Projetos",
    icon="📊",
)

analise3 = st.Page(
    page="pages/03_evolucao_mensal.py",
    title="Evolução Mensal",
    icon="📈",
)

analise4 = st.Page(
    page="pages/04_analise_mensal_taxa_plano.py",
    title="Análise Mensal Taxa/Plano",
    icon="📑",
)

analise5 = st.Page(
    page="pages/05_acumulado_taxa_plano.py",
    title="Acumulado Taxa/Plano",
    icon="🗂️",
)

pg = st.navigation(
    {
        "Análises": [analise1, analise2, analise3, analise4, analise5],
    }
)
pg.run()
