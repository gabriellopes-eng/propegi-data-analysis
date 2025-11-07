# Página: Análise 2 — Somatório dos Valores das Folhas por Projeto
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px

# Adiciona o diretório pai ao path para importar data_utils
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import carregar_financas_json, filtrar  # noqa: E402

CAMINHO_PADRAO_JSON = Path(__file__).resolve().parents[1] / "input" / "Financas.json"

st.set_page_config(page_title="Análise 2", layout="wide", initial_sidebar_state="collapsed")
st.header("◈ Análise 2: Somatório dos valores das folhas por projeto")

caminho = st.text_input("Caminho do arquivo Financas.json", value=str(CAMINHO_PADRAO_JSON), help="Se necessário, ajuste para o local onde o arquivo está.")

try:
	df = carregar_financas_json(caminho)
except Exception as e:
	st.error(f"Erro ao carregar JSON: {e}")
	st.stop()

anos = sorted(df["Ano"].unique().tolist())
col1, col2 = st.columns([2, 3])
with col1:
	anos_sel = st.multiselect("Filtrar por Ano (opcional)", anos, default=anos)
with col2:
	nome_filtro = st.text_input("Filtrar por nome do projeto (contém, opcional)", value="")

df_filt = filtrar(df, anos_sel, None)
if nome_filtro.strip():
	df_filt = df_filt[df_filt["Projetos"].str.contains(nome_filtro, case=False, na=False)]

if df_filt.empty:
	st.warning("Sem dados para os filtros escolhidos.")
	st.stop()

soma_projeto = (
	df_filt.groupby("Projetos", as_index=False)["Valor da folha"]
	.sum()
	.rename(columns={"Valor da folha": "Total"})
	.sort_values("Total", ascending=True)
)

fig = px.bar(soma_projeto, x="Total", y="Projetos", orientation="h", text="Total", labels={"Total": "Total (R$)", "Projetos": "Projetos"})
fig.update_traces(texttemplate="R$ %{x:,.2f}", hovertemplate="Projeto: %{y}<br>Total: R$ %{x:,.2f}<extra></extra>")
fig.update_layout(xaxis_tickformat=",.2f", margin=dict(l=10, r=10, t=30, b=10), height=600)

st.plotly_chart(fig, width='stretch')
st.subheader("◆ Tabela - Somatório por Projeto")
st.dataframe(soma_projeto[["Projetos", "Total"]].style.format({"Total": "{:,.2f}"}), width='stretch', height=450)
