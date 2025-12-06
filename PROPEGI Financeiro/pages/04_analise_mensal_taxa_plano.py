from pathlib import Path
import streamlit as st
import plotly.express as px



# importar data_utils
from data_utils import carregar_dados, filtrar_por_ano

PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

st.set_page_config(page_title="Análise Mensal - Taxa/Plano", layout="wide")
st.header("📊 Análise Mensal por Taxa e Plano de Trabalho")
st.info("""
**Storytelling:**
Esta análise detalha a evolução mensal dos valores por tipo de taxa e plano de trabalho, permitindo identificar a contribuição de cada categoria ao longo do tempo e apoiar decisões de gestão financeira.
""")

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
    projeto_sel = st.selectbox("Selecionar Projeto", projetos_disponiveis)

# aplicar filtros
df_filtrado = filtrar_por_ano(df, anos_sel)
df_filtrado = df_filtrado[df_filtrado["nomeProjeto"] == projeto_sel]

if df_filtrado.empty:
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# agrupar por mês e categoria do recurso
mensal_categoria = (
    df_filtrado.groupby(["mes", "numeroMes", "categoriaDoRecurso"], as_index=False)["valorFloat"]
    .sum()
    .rename(columns={"valorFloat": "Total"})
    .sort_values("numeroMes")
)

# gráfico de barras agrupadas
fig = px.bar(
    mensal_categoria,
    x="mes",
    y="Total",
    color="categoriaDoRecurso",
    barmode="group",
    text="Total",
    labels={
        "mes": "Mês",
        "Total": "Valor (R$)",
        "categoriaDoRecurso": "Categoria"
    },
    color_discrete_map={
        "Taxa": "#EF4444",              
        "Plano de Trabalho": "#3B82F6"  
    },
    category_orders={
        "mes": df_filtrado.sort_values("numeroMes")["mes"].unique().tolist()
    }
)

fig.update_traces(texttemplate="R$ %{y:,.0f}", textposition="outside")
fig.update_layout(
    xaxis_title="Mês",
    yaxis_title="Valor (R$)",
    yaxis_tickformat=",.0f",
    height=500,
    legend_title="Categoria"
)

st.plotly_chart(fig, width='stretch')

# tabela
st.subheader("📋 Tabela Detalhada")
tabela_pivot = mensal_categoria.pivot_table(
    index="mes",
    columns="categoriaDoRecurso",
    values="Total",
    fill_value=0
).reindex(df_filtrado.sort_values("numeroMes")["mes"].unique())

st.dataframe(
    tabela_pivot.style.format("R$ {:,.2f}"),
    width='stretch',
    height=400
)
