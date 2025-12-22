from pathlib import Path
import streamlit as st
import plotly.express as px



# importar data_utils
from data_utils import carregar_dados, filtrar_por_ano

PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

st.set_page_config(page_title="Evolução Mensal", layout="wide")
st.header("Evolução Mensal do Valor Total", divider="blue")
st.info("""
**Storytelling:**
Esta análise apresenta a evolução mensal do valor total recebido, permitindo identificar tendências, sazonalidades e períodos de maior ou menor captação ao longo do tempo.
""")

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

# criar coluna AnoMes para exibição (ex: "2025-Jan")
df_filtrado["AnoMes"] = df_filtrado["ano"].astype(str) + "-" + df_filtrado["mes"]

# agrupar por mês e somar todos os projetos
total_mensal = (
    df_filtrado.groupby(["AnoMes", "numeroMes", "ano"], as_index=False)["valorFloat"]
    .sum()
    .rename(columns={"valorFloat": "Total"})
    .sort_values(["ano", "numeroMes"])
)

# gráfico de barras
fig = px.bar(
    total_mensal,
    x="AnoMes",
    y="Total",
    text="Total",
    labels={"AnoMes": "Mês/Ano", "Total": "Total (R$)"}
)
fig.update_traces(
    texttemplate="R$ %{y:,.2f}",
    hovertemplate="Mês/Ano: %{x}<br>Total (todos os projetos): R$ %{y:,.2f}<extra></extra>"
)
fig.update_layout(
    xaxis_title="Mês/Ano",
    yaxis_title="Total (R$)",
    xaxis_tickangle=-45,
    yaxis_tickformat=",.2f",
    height=600
)

st.plotly_chart(fig, width='stretch')

st.subheader("◈ Tabela - Total Mensal (Todos os projetos)")
st.dataframe(
    total_mensal[["AnoMes", "Total"]].style.format({"Total": "R$ {:,.2f}"}),
    width='stretch',
    height=450
)
