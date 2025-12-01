from pathlib import Path
import streamlit as st
import plotly.express as px

# importar data_utils
from data_utils import carregar_dados, filtrar_por_ano

PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

st.set_page_config(page_title="Acumulado - Taxa/Plano", layout="wide")
st.header("📊 Análise do Período Completo por Taxa e Plano de Trabalho")

# carregar TODOS os JSONs da pasta input
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# filtros
anos_disponiveis = sorted(df["ano"].unique().tolist())
anos_sel = st.multiselect("Filtrar por Ano (opcional)", anos_disponiveis, default=anos_disponiveis)

# aplicar filtro
df_filtrado = filtrar_por_ano(df, anos_sel)

if df_filtrado.empty:
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# agrupar por projeto e categoria do recurso (soma de todos os meses)
acumulado_categoria = (
    df_filtrado.groupby(["nomeProjeto", "categoriaDoRecurso"], as_index=False)["valorFloat"]
    .sum()
    .rename(columns={"valorFloat": "Total"})
)

# gráfico de barras agrupadas
fig = px.bar(
    acumulado_categoria,
    x="nomeProjeto",
    y="Total",
    color="categoriaDoRecurso",
    barmode="group",
    text="Total",
    labels={
        "nomeProjeto": "Projeto",
        "Total": "Valor (R$)",
        "categoriaDoRecurso": "Categoria"
    },
    color_discrete_map={
        "Taxa": "#EF4444",             
        "Plano de Trabalho": "#3B82F6"  
    }
)

fig.update_traces(texttemplate="R$ %{y:,.0f}", textposition="outside")
fig.update_layout(
    xaxis_title="Projeto",
    yaxis_title="Valor Acumulado (R$)",
    yaxis_tickformat=",.0f",
    height=500,
    legend_title="Categoria",
    xaxis_tickangle=-45
)

st.plotly_chart(fig, width='stretch')

# tabela
st.subheader("📋 Tabela Detalhada - Valores Acumulados")
tabela_pivot = acumulado_categoria.pivot_table(
    index="nomeProjeto",
    columns="categoriaDoRecurso",
    values="Total",
    fill_value=0
)

# adicionar coluna de total geral
tabela_pivot["Total Geral"] = tabela_pivot.sum(axis=1)

st.dataframe(
    tabela_pivot.style.format("R$ {:,.2f}"),
    width='stretch',
    height=400
)
