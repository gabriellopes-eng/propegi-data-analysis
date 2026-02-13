from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import load_data, filter_by_year

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
INPUT_FOLDER = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Somatório por Projeto", layout="wide")

# Título principal da página
st.header("Somatório dos Valores por Projeto", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
Esta análise mostra o somatório dos valores recebidos por cada projeto, permitindo identificar quais projetos são mais expressivos em termos de captação de recursos e auxiliando na priorização de esforços e investimentos.
""")

# Carrega os dados da pasta de entrada
# Aqui, todos os arquivos JSON são carregados e combinados em um único DataFrame
try:
    df = load_data(INPUT_FOLDER)
except Exception as e:
    # Exibe uma mensagem de erro e interrompe a execução se houver problemas ao carregar os dados
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Cria uma lista de anos disponíveis para o filtro
available_years = sorted(df["ano"].unique().tolist())

# Interface para seleção de filtros
# Permite ao usuário filtrar os dados por ano e buscar projetos pelo nome
col1, col2 = st.columns([2, 3])
with col1:
    selected_years = st.multiselect("Filtrar por Ano (opcional)", available_years, default=available_years)
with col2:
    name_filter = st.text_input("Filtrar por nome do projeto (contém, opcional)", value="")

# Aplica os filtros selecionados pelo usuário
df_filtered = filter_by_year(df, selected_years)  # Filtra pelos anos selecionados
if name_filter.strip():
    # Filtra os projetos cujo nome contém o texto fornecido (case insensitive)
    df_filtered = df_filtered[df_filtered["nomeProjeto"].str.contains(name_filter, case=False, na=False)]

# Verifica se há dados após os filtros
if df_filtered.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Agrupa os dados por projeto e calcula o somatório dos valores financeiros
project_totals = (
    df_filtered.groupby("nomeProjeto", as_index=False)["valorFloat"]
    .sum()  # Soma os valores financeiros por projeto
    .rename(columns={"valorFloat": "Total"})  # Renomeia a coluna para "Total"
    .sort_values("Total", ascending=True)  # Ordena os projetos pelo total (do menor para o maior)
)

# Cria um gráfico de barras horizontal usando Plotly Express
# O gráfico mostra o total financeiro captado por cada projeto
fig = px.bar(
    project_totals,
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
st.subheader("Tabela - Somatório por Projeto")
st.dataframe(
    project_totals[["nomeProjeto", "Total"]].style.format({"Total": "R$ {:,.2f}"}),  # Formata os valores como moeda
    width='stretch',
    height=450
)
