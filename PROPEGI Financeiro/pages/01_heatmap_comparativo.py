from pathlib import Path
import streamlit as st
import plotly.express as px

# importar data_utils 
from data_utils import carregar_dados, filtrar_por_ano, filtrar_por_projeto

PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

st.set_page_config(page_title="Heatmap Comparativo", layout="wide")
st.header("📊 Comparativo de Valores por Projeto e Mês")

# carregar TODOS os JSONs da pasta input
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# filtros 
anos_disponiveis = sorted(df["ano"].unique().tolist())
projetos_disponiveis = sorted(df["nomeProjeto"].unique().tolist())

col1, col2 = st.columns(2)
with col1:
    anos_sel = st.multiselect("Filtrar por Ano", anos_disponiveis, default=anos_disponiveis)
with col2:
    projetos_sel = st.multiselect("Filtrar por Projeto (opcional)", projetos_disponiveis)

# aplicar filtros
df_filtrado = filtrar_por_ano(df, anos_sel)
if projetos_sel:
    df_filtrado = filtrar_por_projeto(df_filtrado, projetos_sel)

if df_filtrado.empty:
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Pivot para heatmap
tabela = df_filtrado.pivot_table(
    index="nomeProjeto",
    columns="mes",
    values="valorFloat",
    aggfunc="sum",
    fill_value=0
)

# ordenar colunas por número do mês
ordem_meses = df_filtrado[["mes", "numeroMes"]].drop_duplicates().sort_values("numeroMes")["mes"].tolist()
tabela = tabela.reindex(columns=ordem_meses, fill_value=0)

# Heatmap
fig = px.imshow(
    tabela.values,
    labels=dict(x="Mês", y="Projeto", color="Valor (R$)"),
    x=tabela.columns,
    y=tabela.index,
    aspect="auto",
    color_continuous_scale="Blues"
)
fig.update_traces(hovertemplate="Projeto: %{y}<br>Mês: %{x}<br>Valor: R$ %{z:,.2f}<extra></extra>")

st.plotly_chart(fig, width='stretch')

st.subheader("📋 Tabela Resumida")
st.dataframe(tabela.style.format("R$ {:,.2f}"), width='stretch', height=400)
