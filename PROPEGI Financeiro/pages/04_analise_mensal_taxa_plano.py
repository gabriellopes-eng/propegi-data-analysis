"""
Página: Análise — Mensal por Taxa e Plano de Trabalho
Mostra o somatório mensal de "Valor da folha" para um projeto (ou conjunto), separado por Taxa e por Plano de Trabalho.
"""
import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Permitir import do módulo raiz
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import carregar_financas_json, filtrar  # noqa: E402

CAMINHO_PADRAO_JSON = Path(__file__).resolve().parents[1] / "input" / "Financas.json"

st.set_page_config(page_title="Análise Mensal — Taxa/Plano", layout="wide", initial_sidebar_state="collapsed")
st.header("◈ Análise Mensal por Taxa e Plano de Trabalho")

caminho = st.text_input(
    "Caminho do arquivo Financas.json",
    value=str(CAMINHO_PADRAO_JSON),
    help="Se necessário, ajuste para o local onde o arquivo está.",
)

try:
    df = carregar_financas_json(caminho)
except Exception as e:
    st.error(f"Erro ao carregar JSON: {e}")
    st.stop()

# Filtros
anos = sorted(df["Ano"].unique().tolist())
projetos = sorted(df["Projetos"].unique().tolist())

col1, col2 = st.columns([2, 2])
with col1:
    anos_sel = st.multiselect("Filtrar por ano", anos, default=anos)
with col2:
    projeto_sel = st.selectbox("Selecionar projeto (opcional)", options=["(Todos)"] + projetos, index=0)

df_filt = filtrar(df, anos_sel, None)
if projeto_sel != "(Todos)":
    df_filt = df_filt[df_filt["Projetos"] == projeto_sel]

if df_filt.empty:
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Ordenação temporal
ordem = df_filt[["AnoMes", "ord_col"]].drop_duplicates().sort_values("ord_col")

def grafico_empilhado(df_in, coluna_cor, titulo):
    agrupado = (
        df_in.groupby(["AnoMes", "ord_col", coluna_cor], as_index=False)["Valor da folha"].sum()
        .rename(columns={"Valor da folha": "Total"})
        .sort_values(["ord_col", coluna_cor])
    )
    fig = px.bar(
        agrupado,
        x="AnoMes",
        y="Total",
        color=coluna_cor,
        category_orders={"AnoMes": ordem["AnoMes"].tolist()},
        labels={"AnoMes": "Mês/Ano", "Total": "Total (R$)", coluna_cor: coluna_cor},
        title=titulo,
    )
    fig.update_traces(texttemplate=None)
    
    # Adicionar linha de tendência (total mensal)
    total_mensal = (
        df_in.groupby(["AnoMes", "ord_col"], as_index=False)["Valor da folha"].sum()
        .rename(columns={"Valor da folha": "Total_Mensal"})
        .sort_values("ord_col")
    )
    
    fig.add_trace(
        go.Scatter(
            x=total_mensal["AnoMes"],
            y=total_mensal["Total_Mensal"],
            mode="lines+markers",
            name="Total Mensal",
            line=dict(color="orange", width=3),
            marker=dict(size=8, symbol="circle"),
            yaxis="y2"
        )
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(title="Total por Categoria (R$)", tickformat=",.2f"),
        yaxis2=dict(
            title="Total Mensal (R$)",
            overlaying="y",
            side="right",
            tickformat=",.2f"
        ),
        height=500,
        legend_title=coluna_cor,
        hovermode="x unified"
    )
    return fig

colA, colB = st.columns(2)
with colA:
    st.subheader("Mensal por taxa")
    st.plotly_chart(grafico_empilhado(df_filt, "Taxa", "Somatório mensal por taxa"), use_container_width=True)
with colB:
    st.subheader("Mensal por plano de trabalho")
    st.plotly_chart(grafico_empilhado(df_filt, "Plano de Trabalho", "Somatório mensal por plano de trabalho"), use_container_width=True)

st.subheader("◆ Tabela mensal — Taxa × Plano de Trabalho")
tabela = (
    df_filt.groupby(["AnoMes", "ord_col", "Taxa", "Plano de Trabalho"], as_index=False)["Valor da folha"].sum()
    .rename(columns={"Valor da folha": "Total"})
    .sort_values(["ord_col", "Taxa", "Plano de Trabalho"])
)
st.dataframe(tabela[["AnoMes", "Taxa", "Plano de Trabalho", "Total"]].style.format({"Total": "{:,.2f}"}), use_container_width=True, height=450)
