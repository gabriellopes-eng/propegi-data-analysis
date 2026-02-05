from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import carregar_dados, filtrar_por_ano, filtrar_por_projeto

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Comparative Heatmap", layout="wide")

# Título principal da página
st.header("Comparison of Values by Project and Month", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
This analysis presents a visual comparison of the values received by project and by month, making it easier to identify patterns, seasonality, and projects of greater financial relevance over time.
""")

# Carrega os dados da pasta de entrada
# Aqui, todos os arquivos JSON são carregados e combinados em um único DataFrame
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    # Exibe uma mensagem de erro e interrompe a execução se houver problemas ao carregar os dados
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Cria listas de opções para os filtros baseados nos dados carregados
anos_disponiveis = sorted(df["ano"].unique().tolist())  # Lista de anos únicos
projetos_disponiveis = sorted(df["nomeProjeto"].unique().tolist())  # Lista de projetos únicos

# Interface para seleção de filtros
# Permite ao usuário filtrar os dados por ano e projeto
col1, col2 = st.columns(2)
with col1:
    anos_sel = st.multiselect("Filter by Year", anos_disponiveis, default=anos_disponiveis)
with col2:
    projetos_sel = st.multiselect("Filter by Year (optional)", projetos_disponiveis)

# Aplica os filtros selecionados pelo usuário
df_filtrado = filtrar_por_ano(df, anos_sel)  # Filtra pelos anos selecionados
if projetos_sel:
    df_filtrado = filtrar_por_projeto(df_filtrado, projetos_sel)  # Filtra pelos projetos selecionados, se houver

# Verifica se há dados após os filtros
if df_filtrado.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Cria uma tabela dinâmica (pivot table) para organizar os dados no formato necessário para o heatmap
# Index: nome do projeto
# Columns: mês
# Values: soma dos valores financeiros
tabela = df_filtrado.pivot_table(
    index="nomeProjeto",
    columns="mes",
    values="valorFloat",
    aggfunc="sum",
    fill_value=0  # Preenche valores ausentes com 0
)

# Ordena as colunas da tabela pela ordem cronológica dos meses
ordem_meses = df_filtrado[["mes", "numeroMes"]].drop_duplicates().sort_values("numeroMes")["mes"].tolist()
tabela = tabela.reindex(columns=ordem_meses, fill_value=0)

# Cria o heatmap usando Plotly Express
# O heatmap mostra os valores financeiros por projeto (eixo Y) e por mês (eixo X)
fig = px.imshow(
    tabela.values,  # Dados da tabela dinâmica
    labels=dict(x="Mês", y="Projeto", color="Valor (R$)"),  # Rótulos dos eixos e da legenda
    x=tabela.columns,  # Nomes das colunas (meses)
    y=tabela.index,  # Nomes das linhas (projetos)
    aspect="auto",  # Ajusta automaticamente o aspecto do gráfico
    color_continuous_scale="Blues"  # Escala de cores em tons de azul
)

# Personaliza o texto exibido ao passar o mouse sobre o gráfico
fig.update_traces(hovertemplate="Projeto: %{y}<br>Mês: %{x}<br>Valor: R$ %{z:,.2f}<extra></extra>")

# Exibe o heatmap na página
st.plotly_chart(fig, width='stretch')

# Exibe a tabela resumida abaixo do gráfico
# A tabela mostra os mesmos dados do heatmap, mas em formato tabular
st.subheader("Summary Table")
st.dataframe(tabela.style.format("R$ {:,.2f}"), width='stretch', height=400)
