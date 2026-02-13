from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import load_data, filter_by_year, filter_by_project

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
INPUT_FOLDER = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Heatmap Comparativo", layout="wide")

# Título principal da página
st.header("Comparativo de Valores por Projeto e Mês", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
Esta análise apresenta um comparativo visual dos valores recebidos por projeto e por mês, facilitando a identificação de padrões, sazonalidades e projetos de maior relevância financeira ao longo do tempo.
""")

# Carrega os dados da pasta de entrada
# Aqui, todos os arquivos JSON são carregados e combinados em um único DataFrame
try:
    df = load_data(INPUT_FOLDER)
except Exception as e:
    # Exibe uma mensagem de erro e interrompe a execução se houver problemas ao carregar os dados
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Cria listas de opções para os filtros baseados nos dados carregados
available_years = sorted(df["ano"].unique().tolist())  # Lista de anos únicos
available_projects = sorted(df["nomeProjeto"].unique().tolist())  # Lista de projetos únicos

# Interface para seleção de filtros
# Permite ao usuário filtrar os dados por ano e projeto
col1, col2 = st.columns(2)
with col1:
    selected_years = st.multiselect("Filtrar por Ano", available_years, default=available_years)
with col2:
    selected_projects = st.multiselect("Filtrar por Ano (opcional)", available_projects)

# Aplica os filtros selecionados pelo usuário
df_filtered = filter_by_year(df, selected_years)  # Filtra pelos anos selecionados
if selected_projects:
    df_filtered = filter_by_project(df_filtered, selected_projects)  # Filtra pelos projetos selecionados, se houver

# Verifica se há dados após os filtros
if df_filtered.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Cria uma tabela dinâmica (pivot table) para organizar os dados no formato necessário para o heatmap
# Index: nome do projeto
# Columns: mês
# Values: soma dos valores financeiros
pivot_table = df_filtered.pivot_table(
    index="nomeProjeto",
    columns="mes",
    values="valorFloat",
    aggfunc="sum",
    fill_value=0  # Preenche valores ausentes com 0
)

# Ordena as colunas da tabela pela ordem cronológica dos meses
ordem_meses = df_filtered[["mes", "numeroMes"]].drop_duplicates().sort_values("numeroMes")["mes"].tolist()
pivot_table = pivot_table.reindex(columns=ordem_meses, fill_value=0)

# Cria o heatmap usando Plotly Express
# O heatmap mostra os valores financeiros por projeto (eixo Y) e por mês (eixo X)
fig = px.imshow(
    pivot_table.values,  # Dados da tabela dinâmica
    labels=dict(x="Mês", y="Projeto", color="Valor (R$)"),  # Rótulos dos eixos e da legenda
    x=pivot_table.columns,  # Nomes das colunas (meses)
    y=pivot_table.index,  # Nomes das linhas (projetos)
    aspect="auto",  # Ajusta automaticamente o aspecto do gráfico
    color_continuous_scale="Blues"  # Escala de cores em tons de azul
)

# Personaliza o texto exibido ao passar o mouse sobre o gráfico
fig.update_traces(hovertemplate="Projeto: %{y}<br>Mês: %{x}<br>Valor: R$ %{z:,.2f}<extra></extra>")

# Exibe o heatmap na página
st.plotly_chart(fig, width='stretch')

# Exibe a tabela resumida abaixo do gráfico
# A tabela mostra os mesmos dados do heatmap, mas em formato tabular
st.subheader("Tabela Resumida")
st.dataframe(pivot_table.style.format("R$ {:,.2f}"), width='stretch', height=400)
