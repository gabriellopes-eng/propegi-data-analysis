from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import carregar_dados, filtrar_por_ano

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Monthly Evolution", layout="wide")

# Título principal da página
st.header("Monthly Evolution of Total Value", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
This analysis presents the monthly evolution of the total value received, allowing you to identify trends, seasonality, and periods of higher or lower fundraising over time.
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
# Permite ao usuário filtrar os dados por ano
anos_sel = st.multiselect("Filter by Year (optional)", anos_disponiveis, default=anos_disponiveis)

# Aplica o filtro de ano selecionado pelo usuário
df_filtrado = filtrar_por_ano(df, anos_sel)

# Verifica se há dados após os filtros
if df_filtrado.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Cria uma coluna "AnoMes" para exibição no formato "2025-Jan"
# Essa coluna será usada para organizar os dados no gráfico e na tabela
df_filtrado["AnoMes"] = df_filtrado["ano"].astype(str) + "-" + df_filtrado["mes"]

# Agrupa os dados por mês e soma os valores de todos os projetos
# Isso gera o total financeiro mensal para todos os projetos combinados
total_mensal = (
    df_filtrado.groupby(["AnoMes", "numeroMes", "ano"], as_index=False)["valorFloat"]
    .sum()  # Soma os valores financeiros por mês
    .rename(columns={"valorFloat": "Total"})  # Renomeia a coluna para "Total"
    .sort_values(["ano", "numeroMes"])  # Ordena os dados por ano e número do mês
)

# Cria um gráfico de barras usando Plotly Express
# O gráfico mostra a evolução mensal do valor total recebido
fig = px.bar(
    total_mensal,
    x="AnoMes",  # Mês/Ano no eixo X
    y="Total",  # Total financeiro no eixo Y
    text="Total",  # Exibe os valores diretamente nas barras
    labels={"AnoMes": "Mês/Ano", "Total": "Total (R$)"}  # Rótulos dos eixos
)

# Personaliza o texto exibido no gráfico e o comportamento do hover
fig.update_traces(
    texttemplate="R$ %{y:,.2f}",  # Formata os valores exibidos nas barras
    hovertemplate="Mês/Ano: %{x}<br>Total (todos os projetos): R$ %{y:,.2f}<extra></extra>"  # Formata o texto ao passar o mouse
)

# Ajusta o layout do gráfico
fig.update_layout(
    xaxis_title="Mês/Ano",  # Título do eixo X
    yaxis_title="Total (R$)",  # Título do eixo Y
    xaxis_tickangle=-45,  # Inclina os rótulos do eixo X para melhor leitura
    yaxis_tickformat=",.2f",  # Formata os valores do eixo Y como moeda
    height=600  # Define a altura do gráfico
)

# Exibe o gráfico na página
st.plotly_chart(fig, width='stretch')

# Exibe uma tabela com o total mensal
# A tabela mostra os mesmos dados do gráfico, mas em formato tabular
st.subheader("Table - Monthly Totals (All projects)")
st.dataframe(
    total_mensal[["AnoMes", "Total"]].style.format({"Total": "R$ {:,.2f}"}),  # Formata os valores como moeda
    width='stretch',
    height=450
)