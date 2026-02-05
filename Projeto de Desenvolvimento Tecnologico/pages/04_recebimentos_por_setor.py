import streamlit as st
import plotly.express as px
import pandas as pd

from data_utils import (
    carregar_ultimo_backup_json,
    normalize_values,
    prepare_dates,
)

st.set_page_config(layout="wide")
st.header("Recebimentos por ano por Setor (Segmento)", divider="blue")
st.info("""
**Storytelling:**
Esta análise detalha os recebimentos por setor (segmento) ao longo dos anos, permitindo identificar quais setores são mais relevantes em termos de captação de recursos. Isso auxilia na definição de estratégias para fortalecer setores-chave e diversificar fontes de receita.
""")


# --- Carregamento e preparo (dinâmico) ---
df = carregar_ultimo_backup_json()
if df is None or (hasattr(df, 'empty') and df.empty):
    st.error("Backup não pôde ser carregado ou está vazio.")
    st.stop()
if isinstance(df, list):
    import pandas as pd
    df = pd.DataFrame(df)
if df.empty or 'dataPublicacao' not in df.columns:
    st.error("Dados inválidos ou coluna 'dataPublicacao' ausente no backup.")
    st.stop()
df = normalize_values(df)
df = prepare_dates(df)

if "segmento" not in df.columns:
    st.error("❌ A coluna 'Segmento' não foi encontrada no JSON.")
    st.stop()

# Total por registro (Agência + Unidade + IA-UPE)
value_cols = ["valorAgencia", "valorUnidade", "valorIAUPE"]
df["ValorTotal"] = df[value_cols].sum(axis=1)

# Agrupamento Ano × Segmento (soma valores)
df_group = (
    df.groupby(["Ano", "segmento"], as_index=False)["ValorTotal"]
      .sum()
      .sort_values(["Ano", "segmento"])
)

# --- Layout: gráfico (esq) + controles/pizza (dir) ---
col_chart, col_side = st.columns([7, 5], gap="large")

with col_chart:
    st.subheader("Recebimentos anuais por Setor (Segmento)")
    fig_bar = px.bar(
        df_group,
        x="Ano",
        y="ValorTotal",
        color="segmento",
        barmode="group",
        text_auto=".2s",
        labels={"ValorTotal": "Valor (R$)"},
        title=None,
    )
    fig_bar.update_layout(xaxis=dict(type="category"))
    st.plotly_chart(fig_bar, width='stretch')

with col_side:
    st.subheader("Distribuição por setor")
    available_years = sorted(df_group["Ano"].unique().astype(int).tolist(), reverse=True)
    selected_year = st.selectbox("Período", available_years, index=0)

    df_year = df_group[df_group["Ano"] == selected_year].copy()
    if df_year.empty:
        st.info("Sem dados para o ano selecionado.")
    else:
        fig_pie = px.pie(
            df_year,
            names="segmento",
            values="ValorTotal",
            hole=0.50,
            title=f"Distribuição por setor — {selected_year}",
        )
    st.plotly_chart(fig_pie, width='stretch')

# --- Tabela ---
with st.expander("Ver tabela por ano e setor"):
    pivot_table = (
        df_group.pivot(index="Ano", columns="segmento", values="ValorTotal")
               .fillna(0.0)
               .sort_index(axis=1)  # ordena colunas alfabeticamente
    )
    st.dataframe(pivot_table, width='stretch')
