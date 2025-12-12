import streamlit as st

# Adiciona um título ao app principal
st.set_page_config(page_title="Projeto de Desenvolvimento Tecnológico", page_icon="../images/upeLogo.png", layout="wide")

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

analise1 = st.Page(
    page="pages/01_recebimentos_mensais.py",
    title="Recebimentos mensais — Agência / Unidade / IA-UPE",
    icon=":material/finance_mode:",
    default=True, # Define esta como a página inicial
)

analise2 = st.Page(
    page="pages/02_projetos_por_segmento.py",
    title="Projetos em desenvolvimento por segmento/ano",
    icon=":material/bar_chart_4_bars:",
)

analise3 = st.Page(
    page="pages/03_recebimentos_anuais.py",
    title="Recebimentos anuais por órgão",
    icon=":material/bar_chart:",
)

analise4 = st.Page(
    page="pages/04_recebimentos_por_setor.py",
    title="Recebimentos por setor (segmento)",
    icon=":material/pie_chart:",
)

analise5 = st.Page(
    page="pages/05_analise_temporal.py",
    title="Análise Temporal",
    icon=":material/account_tree:",
)

# Cria a navegação com uma lista de páginas
pg = st.navigation(
    {
        "Análises": [analise1, analise2, analise3, analise4, analise5],
    }
)

# Executa a página selecionada
pg.run()