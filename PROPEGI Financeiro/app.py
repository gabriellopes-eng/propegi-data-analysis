import streamlit as st
import os

# Configuração inicial da aplicação Streamlit
# Define o título da aba do navegador, o ícone e o layout da página como "wide" (tela cheia)
st.set_page_config(page_title="PROPEGI Financial", page_icon="../images/upeLogo.png", layout="wide")

# Título principal da aplicação exibido no topo da página
st.title("PROPEGI Financial")

# Adiciona um logo na barra lateral para reforçar a identidade visual da aplicação
with st.sidebar:
    col1, col2, col3 = st.columns([1, 3, 1])  # Divide a barra lateral em 3 colunas para centralizar o logo
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'upeLogo.png')  # Caminho do logo
    with col2:  # Coluna central para exibir o logo
        if os.path.exists(logo_path):  # Verifica se o arquivo do logo existe
            st.image(logo_path, width=150)  # Exibe o logo com largura de 150px
        else:
            st.warning("UPE logo not found in images/upeLogo.png")  # Exibe um aviso se o logo não for encontrado

# Configuração de navegação entre páginas
# Cada página representa uma análise específica do sistema financeiro
# Isso permite que o usuário navegue facilmente entre diferentes visualizações e relatórios

# Página 1: Heatmap Comparativo
# Mostra uma análise visual comparativa em formato de mapa de calor
analysis1 = st.Page(
    page="pages/01_heatmap_comparativo.py",
    title="Comparative Heatmap",
    icon="🌡️",
    default=True,  # Define esta página como a padrão ao abrir o aplicativo
)

# Página 2: Somatório de Projetos
# Exibe o total acumulado de projetos, provavelmente agrupados por categorias ou períodos
analysis2 = st.Page(
    page="pages/02_somatorio_projetos.py",
    title="Project Totals",
    icon="📊",
)

# Página 3: Evolução Mensal
# Mostra a evolução dos dados financeiros ao longo dos meses
analysis3 = st.Page(
    page="pages/03_evolucao_mensal.py",
    title="Monthly Evolution",
    icon="📈",
)

# Página 4: Análise Mensal Taxa/Plano
# Analisa taxas e planos mensalmente, útil para identificar tendências ou padrões
analysis4 = st.Page(
    page="pages/04_analise_mensal_taxa_plano.py",
    title="Monthly Analysis - Fee/Work Plan",
    icon="📑",
)

# Página 5: Acumulado Taxa/Plano
# Exibe o acumulado de taxas e planos, provavelmente para análises de longo prazo
analysis5 = st.Page(
    page="pages/05_acumulado_taxa_plano.py",
    title="Accumulated - Fee/Work Plan",
    icon="🗂️",
)

# Cria a navegação entre as páginas
# O menu de navegação agrupa todas as análises em uma seção chamada "Analyses"
pg = st.navigation(
    {
        "Analyses": [analysis1, analysis2, analysis3, analysis4, analysis5],
    }
)

# Executa a navegação, permitindo que o usuário alterne entre as páginas configuradas
pg.run()