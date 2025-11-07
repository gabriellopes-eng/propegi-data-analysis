# Página: Análise 1 — Comparativo de Valores das Folhas por Projeto (Heatmap)
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import pandas as pd

# Adiciona o diretório pai ao path para importar data_utils
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import carregar_financas_json, filtrar  # noqa: E402

CAMINHO_PADRAO_JSON = Path(__file__).resolve().parents[1] / "input" / "Financas.json"

st.set_page_config(page_title="Análise 1", layout="wide", initial_sidebar_state="collapsed")
st.header("◈ Comparativo de Valores das Folhas por Projeto com base no Mês e o Ano")

# Entrada do caminho do JSON
caminho = st.text_input("Caminho do arquivo Financas.json", value=str(CAMINHO_PADRAO_JSON), help="Altere caso seu arquivo esteja em outro local.")

try:
	df = carregar_financas_json(caminho)
except Exception as e:
	st.error(f"Erro ao carregar JSON: {e}")
	st.stop()

# Filtros
anos_unicos = sorted(df["Ano"].unique().tolist())
projetos_unicos = sorted(df["Projetos"].unique().tolist())

col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
with col_f1:
	anos_sel = st.multiselect("Filtrar por Ano (opcional)", anos_unicos, default=anos_unicos)
with col_f2:
	projetos_sel = st.multiselect("Filtrar por Projetos (opcional)", projetos_unicos)
with col_f3:
	if st.button("Limpar filtros"):
		anos_sel = anos_unicos
		projetos_sel = []

df_filt = filtrar(df, anos_sel, projetos_sel)
if df_filt.empty:
	st.warning("Sem dados para os filtros escolhidos.")
	st.stop()

# Pivot para Heatmap
ord_cols = df_filt[["AnoMes", "ord_col"]].drop_duplicates().sort_values("ord_col")
ordem_colunas = ord_cols["AnoMes"].tolist()

tabela = (
	df_filt.groupby(["Projetos", "AnoMes"], as_index=False)["Valor da folha"]
	.sum()
	.pivot(index="Projetos", columns="AnoMes", values="Valor da folha")
	.reindex(columns=ordem_colunas)
	.fillna(0.0)
)

fig = px.imshow(
	tabela.values,
	labels=dict(x="Mês/Ano", y="Projetos", color="R$"),
	x=tabela.columns,
	y=tabela.index,
	aspect="auto",
	color_continuous_scale="Blues",
)
fig.update_traces(hovertemplate="Projeto: %{y}<br>Mês/Ano: %{x}<br>Valor: R$ %{z:,.2f}<extra></extra>")
fig.update_coloraxes(colorbar_title="Valor (R$)")

st.plotly_chart(fig, width='stretch')

st.subheader("◆ Tabela Resumida")
st.dataframe(tabela.style.format("{:,.2f}"), width='stretch', height=400)

