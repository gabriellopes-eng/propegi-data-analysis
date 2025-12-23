import streamlit as st

# Adiciona um título ao app principal
st.set_page_config(page_title="Technological Development Project", page_icon="../images/upeLogo.png", layout="wide")

st.title("Technological Development Project")

# Imagem centralizada na barra lateral
import os
with st.sidebar:
    # Cria três colunas na barra lateral, sendo a segunda mais larga
    col1, col2, col3 = st.columns([1, 3, 1])

    # Caminho robusto para a imagem
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'upeLogo.png')
    # Coloca a imagem na coluna do meio (col2), se existir
    with col2:
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        else:
            st.warning("Logo da UPE não encontrado em images/upeLogo.png")

analysis1 = st.Page(
    page="pages/01_recebimentos_mensais.py",
    title="Recebimentos mensais — Agência / Unidade / IA-UPE",
    icon=":material/finance_mode:",
    default=True, # Define esta como a página inicial
)

analysis2 = st.Page(
    page="pages/02_projetos_por_segmento.py",
    title="Projetos em desenvolvimento por segmento/ano",
    icon=":material/bar_chart_4_bars:",
)

analysis3 = st.Page(
    page="pages/03_recebimentos_anuais.py",
    title="Recebimentos anuais por órgão",
    icon=":material/bar_chart:",
)

analysis4 = st.Page(
    page="pages/04_recebimentos_por_setor.py",
    title="Recebimentos por setor (segmento)",
    icon=":material/pie_chart:",
)

analysis5 = st.Page(
    page="pages/05_analise_temporal.py",
    title="Análise Temporal",
    icon=":material/account_tree:",
)

# Cria a navegação com uma lista de páginas
nav = st.navigation(
    {
        "Análises": [analysis1, analysis2, analysis3, analysis4, analysis5],
    }
)

# Executa a página selecionada
nav.run()