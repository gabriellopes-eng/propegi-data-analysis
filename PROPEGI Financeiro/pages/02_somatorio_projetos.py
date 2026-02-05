from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import carregar_dados, filtrar_por_ano

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Project Totals", layout="wide")

# Título principal da página
st.header("Total Values by Project", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
This analysis shows the total values received by each project, allowing you to identify which projects are the most significant in terms of fundraising and helping to prioritize efforts and investments.
""")

# Carrega os dados da pasta de entrada
# Aqui, todos os arquivos JSON são carregados e combinados em um único DataFrame
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    # Exibe uma mensagem de erro e interrompe a execução se houver problemas ao carregar os dados
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Cria uma lista de anos disponíveis para o filtro
anos_disponiveis = sorted(df["ano"].unique().tolist())

# Interface para seleção de filtros
# Permite ao usuário filtrar os dados por ano e buscar projetos pelo nome
col1, col2 = st.columns([2, 3])
with col1:
    anos_sel = st.multiselect("Filter by Year (optional)", anos_disponiveis, default=anos_disponiveis)
with col2:
    nome_filtro = st.text_input("Filter by Project Name (contains, optional)", value="")

# Aplica os filtros selecionados pelo usuário
df_filtrado = filtrar_por_ano(df, anos_sel)  # Filtra pelos anos selecionados
if nome_filtro.strip():
    # Filtra os projetos cujo nome contém o texto fornecido (case insensitive)
    df_filtrado = df_filtrado[df_filtrado["nomeProjeto"].str.contains(nome_filtro, case=False, na=False)]

# Verifica se há dados após os filtros
if df_filtrado.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Agrupa os dados por projeto e calcula o somatório dos valores financeiros
soma_projeto = (
    df_filtrado.groupby("nomeProjeto", as_index=False)["valorFloat"]
    .sum()  # Soma os valores financeiros por projeto
    .rename(columns={"valorFloat": "Total"})  # Renomeia a coluna para "Total"
    .sort_values("Total", ascending=True)  # Ordena os projetos pelo total (do menor para o maior)
)

# Cria um gráfico de barras horizontal usando Plotly Express
# O gráfico mostra o total financeiro captado por cada projeto
fig = px.bar(
    soma_projeto,
    x="Total",  # Valores financeiros no eixo X
    y="nomeProjeto",  # Nomes dos projetos no eixo Y
    orientation="h",  # Gráfico horizontal
    text="Total",  # Exibe os valores diretamente nas barras
    labels={"Total": "Total (R$)", "nomeProjeto": "Projetos"}  # Rótulos dos eixos
)

# Personaliza o texto exibido no gráfico e o comportamento do hover
fig.update_traces(
    texttemplate="R$ %{x:,.2f}",  # Formata os valores exibidos nas barras
    hovertemplate="Projeto: %{y}<br>Total: R$ %{x:,.2f}<extra></extra>"  # Formata o texto ao passar o mouse
)

# Ajusta o layout do gráfico
fig.update_layout(xaxis_tickformat=",.2f", height=600)  # Formata os valores do eixo X e define a altura do gráfico

# Exibe o gráfico na página
st.plotly_chart(fig, width='stretch')

# Exibe uma tabela com o somatório por projeto
# A tabela mostra os mesmos dados do gráfico, mas em formato tabular
st.subheader("Table - Project Totals")
st.dataframe(
    soma_projeto[["nomeProjeto", "Total"]].style.format({"Total": "R$ {:,.2f}"}),  # Formata os valores como moeda
    width='stretch',
    height=450
)
