import streamlit as st
import plotly.express as px
import pandas as pd

from data_utils import (
    carregar_ultimo_backup_json,  # dinâmico!
    normalizar_valores,
    preparar_datas,
)

st.set_page_config(layout="wide")
st.header("◈ Recebimentos por ano por Setor (Segmento)", divider="blue")
st.info("""
**Storytelling:**
Esta análise detalha os recebimentos por setor (segmento) ao longo dos anos, permitindo identificar quais setores são mais relevantes em termos de captação de recursos. Isso auxilia na definição de estratégias para fortalecer setores-chave e diversificar fontes de receita.
""")


# --- Carregamento e preparo (dinâmico) ---
import streamlit as st
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
df = normalizar_valores(df)
df = preparar_datas(df)

if "segmento" not in df.columns:
    st.error("❌ A coluna 'Segmento' não foi encontrada no JSON.")
    st.stop()

# Total por registro (Agência + Unidade + IA-UPE)
cols_valor = ["valorAgencia", "valorUnidade", "valorIAUPE"]
df["ValorTotal"] = df[cols_valor].sum(axis=1)

# Agrupamento Ano × Segmento (soma valores)
df_group = (
    df.groupby(["Ano", "segmento"], as_index=False)["ValorTotal"]
      .sum()
      .sort_values(["Ano", "segmento"])
)

# --- Layout: gráfico (esq) + controles/pizza (dir) ---
col_chart, col_side = st.columns([7, 5], gap="large")

with col_chart:
    st.subheader("❖ Recebimentos anuais por Setor (Segmento)")
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
    st.subheader("❖ Distribuição por setor")
    anos = sorted(df_group["Ano"].unique().tolist())
    ano_sel = st.selectbox("Período", anos, index=len(anos) - 1)

    df_ano = df_group[df_group["Ano"] == ano_sel].copy()
    if df_ano.empty:
        st.info("Sem dados para o ano selecionado.")
    else:
        fig_pie = px.pie(
            df_ano,
            names="segmento",
            values="ValorTotal",
            hole=0.50,
            title=f"Distribuição por setor — {ano_sel}",
        )
    st.plotly_chart(fig_pie, width='stretch')

# --- Tabela ---
with st.expander("◆ Ver tabela por ano e setor"):
    tabela = (
        df_group.pivot(index="Ano", columns="segmento", values="ValorTotal")
               .fillna(0.0)
               .sort_index(axis=1)  # ordena colunas alfabeticamente
    )
    st.dataframe(tabela, width='stretch')
