from pathlib import Path
import streamlit as st
import plotly.express as px

# importar data_utils
from data_utils import carregar_dados, filtrar_por_ano

PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

st.set_page_config(page_title="Somatório por Projeto", layout="wide")
st.header("💰 Somatório dos Valores por Projeto")

# carregar TODOS os JSONs da pasta input
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# filtros
anos_disponiveis = sorted(df["ano"].unique().tolist())

col1, col2 = st.columns([2, 3])
with col1:
    anos_sel = st.multiselect("Filtrar por Ano (opcional)", anos_disponiveis, default=anos_disponiveis)
with col2:
    nome_filtro = st.text_input("Filtrar por nome do projeto (contém, opcional)", value="")

# aplicar filtros
df_filtrado = filtrar_por_ano(df, anos_sel)
if nome_filtro.strip():
    df_filtrado = df_filtrado[df_filtrado["nomeProjeto"].str.contains(nome_filtro, case=False, na=False)]

if df_filtrado.empty:
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# agrupar e somar por projeto
soma_projeto = (
    df_filtrado.groupby("nomeProjeto", as_index=False)["valorFloat"]
    .sum()
    .rename(columns={"valorFloat": "Total"})
    .sort_values("Total", ascending=True)
)

# gráfico de barras horizontal
fig = px.bar(
    soma_projeto,
    x="Total",
    y="nomeProjeto",
    orientation="h",
    text="Total",
    labels={"Total": "Total (R$)", "nomeProjeto": "Projetos"}
)
fig.update_traces(
    texttemplate="R$ %{x:,.2f}",
    hovertemplate="Projeto: %{y}<br>Total: R$ %{x:,.2f}<extra></extra>"
)
fig.update_layout(xaxis_tickformat=",.2f", height=600)

st.plotly_chart(fig, width='stretch')

st.subheader("📋 Tabela - Somatório por Projeto")
st.dataframe(
    soma_projeto[["nomeProjeto", "Total"]].style.format({"Total": "R$ {:,.2f}"}),
    width='stretch',
    height=450
)
