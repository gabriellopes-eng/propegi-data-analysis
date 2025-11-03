# Página: Análise 3 — Evolução Mensal do Valor Total das Folhas (Todos os projetos)
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

sys.path.append(str(Path(__file__).resolve().parents[1]))
from data_utils import carregar_financas_json, filtrar  # noqa: E402

DEFAULT_JSON_PATH = Path(__file__).resolve().parents[2] / "input" / "Financas.json"

st.set_page_config(page_title="Análise 3", layout="wide", initial_sidebar_state="collapsed")
st.header("◈ Análise 3: Evolução Mensal do Valor Total das Folhas por Projeto")

caminho = st.text_input("Caminho do Financas.json", value=str(DEFAULT_JSON_PATH), help="Se necessário, ajuste para o local onde o arquivo está.")

try:
	df = carregar_financas_json(caminho)
except Exception as e:
	st.error(f"Erro ao carregar JSON: {e}")
	st.stop()

anos_disponiveis = sorted(df["Ano"].unique().tolist())
anos_sel = st.multiselect("Filtrar por Ano (opcional)", anos_disponiveis, default=anos_disponiveis)

df_filt = filtrar(df, anos_sel, None)
if df_filt.empty:
	st.warning("Sem dados para os filtros escolhidos.")
	st.stop()

ordem = df_filt[["AnoMes", "ord_col"]].drop_duplicates().sort_values("ord_col")
ordem_cols = ordem["AnoMes"].tolist()

total_mensal = (
	df_filt.groupby("AnoMes", as_index=False)["Valor da folha"]
	.sum()
	.rename(columns={"Valor da folha": "Total"})
	.merge(ordem, on="AnoMes", how="left")
	.sort_values("ord_col")
)

fig = px.bar(total_mensal, x="AnoMes", y="Total", text="Total", labels={"AnoMes": "Mês/Ano", "Total": "Total (R$)"})
fig.update_traces(texttemplate="R$ %{y:,.2f}", hovertemplate="Mês/Ano: %{x}<br>Total (todos os projetos): R$ %{y:,.2f}<extra></extra>")
fig.update_layout(xaxis_title="Mês/Ano", yaxis_title="Total (R$)", xaxis_tickangle=-45, yaxis_tickformat=",.2f", margin=dict(l=10, r=10, t=30, b=10), height=600)

st.plotly_chart(fig, use_container_width=True)
st.subheader("◆ Tabela - Total Mensal (Todos os projetos)")
st.dataframe(total_mensal[["AnoMes", "Total"]].style.format({"Total": "{:,.2f}"}), use_container_width=True, height=450)
