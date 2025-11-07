import streamlit as st
import plotly.express as px
import pandas as pd

from data_utils import (          # <- import ABSOLUTO
    carregar_json,
    normalizar_valores,
    preparar_datas,
    input_path,                   # <- resolve caminho dentro de input/
    DEFAULT_JSON_NAME,            # <- nome padrão do JSON
)

st.set_page_config(layout="wide")
st.title("◈ Recebimentos por ano por Setor (Segmento)")

# --- Carregamento e preparo ---
df = carregar_json(input_path(DEFAULT_JSON_NAME))
df = normalizar_valores(df)
df = preparar_datas(df)

if "Segmento" not in df.columns:
    st.error("❌ A coluna 'Segmento' não foi encontrada no JSON.")
    st.stop()

# Total por registro (Agência + Unidade + IA-UPE)
cols_valor = ["Valor agência", "Valor unidade", "Valor IA-UPE"]
df["ValorTotal"] = df[cols_valor].sum(axis=1)

# Agrupamento Ano × Segmento (soma valores)
df_group = (
    df.groupby(["Ano", "Segmento"], as_index=False)["ValorTotal"]
      .sum()
      .sort_values(["Ano", "Segmento"])
)

# --- Layout: gráfico (esq) + controles/pizza (dir) ---
col_chart, col_side = st.columns([7, 5], gap="large")

with col_chart:
    st.subheader("❖ Recebimentos anuais por Setor (Segmento)")
    fig_bar = px.bar(
        df_group,
        x="Ano",
        y="ValorTotal",
        color="Segmento",
        barmode="group",
        text_auto=".2s",
        labels={"ValorTotal": "Valor (R$)"},
        title=None,
    )
    fig_bar.update_layout(xaxis=dict(type="category"))
    st.plotly_chart(fig_bar, width='stretch')

with col_side:
    st.subheader("❖ Distribuição por setor")
    anos = sorted(df_group["Ano"].unique().tolist())
    ano_sel = st.selectbox("Período", anos, index=len(anos) - 1)

    df_ano = df_group[df_group["Ano"] == ano_sel].copy()
    if df_ano.empty:
        st.info("Sem dados para o ano selecionado.")
    else:
        fig_pie = px.pie(
            df_ano,
            names="Segmento",
            values="ValorTotal",
            hole=0.50,
            title=f"Distribuição por setor — {ano_sel}",
        )
    st.plotly_chart(fig_pie, width='stretch')

# --- Tabela ---
with st.expander("◆ Ver tabela por ano e setor"):
    tabela = (
        df_group.pivot(index="Ano", columns="Segmento", values="ValorTotal")
               .fillna(0.0)
               .sort_index(axis=1)  # ordena colunas alfabeticamente
    )
    st.dataframe(tabela, width='stretch')
