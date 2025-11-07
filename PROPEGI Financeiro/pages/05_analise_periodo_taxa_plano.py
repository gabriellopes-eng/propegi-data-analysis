import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

# Permitir import do módulo raiz
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import carregar_financas_json, filtrar, validar_financas_df  # noqa: E402

CAMINHO_PADRAO_JSON = Path(__file__).resolve().parents[1] / "input" / "Financas.json"

st.set_page_config(page_title="Análise do Período — Taxa/Plano", layout="wide", initial_sidebar_state="collapsed")
st.header("◈ Análise do Período Completo por Taxa e Plano de Trabalho")

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

# Validações simples do JSON 2024–2025
issues = validar_financas_df(df)
if issues:
    for msg in issues:
        st.warning(msg, icon="⚠️")
else:
    st.caption("Dados carregados e validados.")

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

# Gráfico por Taxa (período)
tot_taxa = (
    df_filt.groupby(["Taxa"], as_index=False)["Valor da folha"].sum()
    .rename(columns={"Valor da folha": "Total"})
    .sort_values("Total", ascending=False)
)
fig_taxa = px.bar(tot_taxa, x="Taxa", y="Total", text="Total", labels={"Total": "Total (R$)"}, title="Total do período por taxa")
fig_taxa.update_traces(texttemplate="R$ %{y:,.2f}")
fig_taxa.update_layout(yaxis_tickformat=",.2f", height=500)

# Gráfico por Plano de Trabalho (período)
tot_plano = (
    df_filt.groupby(["Plano de Trabalho"], as_index=False)["Valor da folha"].sum()
    .rename(columns={"Valor da folha": "Total"})
    .sort_values("Total", ascending=False)
)
fig_plano = px.bar(tot_plano, x="Plano de Trabalho", y="Total", text="Total", labels={"Total": "Total (R$)"}, title="Total do período por plano de trabalho")
fig_plano.update_traces(texttemplate="R$ %{y:,.2f}")
fig_plano.update_layout(yaxis_tickformat=",.2f", height=500)

colA, colB = st.columns(2)
with colA:
    st.subheader("Período por taxa")
    st.plotly_chart(fig_taxa, width='stretch')
with colB:
    st.subheader("Período por plano de trabalho")
    st.plotly_chart(fig_plano, width='stretch')

st.subheader("◆ Tabela — Total do período por Taxa × Plano de Trabalho")
tot_par = (
    df_filt.groupby(["Taxa", "Plano de Trabalho"], as_index=False)["Valor da folha"].sum()
    .rename(columns={"Valor da folha": "Total"})
    .sort_values(["Taxa", "Plano de Trabalho"]) 
)
st.dataframe(tot_par.style.format({"Total": "{:,.2f}"}), width='stretch', height=450)

# Construindo os cards dos últimos 5 acordos firmados
st.divider()
st.subheader("📋 Últimos 5 Acordos Firmados")

ultimos_5 = df.sort_values("ord_col", ascending=False).head(5)

cols = st.columns(5)

for idx, (_, row) in enumerate(ultimos_5.iterrows()):
    with cols[idx]:
        detalhes = (
            f"Taxa: {row.get('Taxa','N/A')} | Plano: {row.get('Plano de Trabalho','N/A')} | "
            f"Status: {row.get('Status','N/A')} | SEI: {row.get('SEI','N/A')}"
        )
        projeto_nome = str(row['Projetos'])[:25] + "..." if len(str(row['Projetos'])) > 25 else str(row['Projetos'])
        # Reuso de estilo do outro dashboard (definição da função pode estar em outro arquivo)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius:8px; padding:16px; color:white;">
              <div style="font-size:12px; opacity:0.9;">📅 {row['AnoMes']}</div>
              <div style="font-size:26px; font-weight:bold; margin:8px 0;">R$ {float(row['Valor da folha']):,.2f}</div>
              <div style="font-size:11px; opacity:0.8; margin-bottom:6px;">{projeto_nome}</div>
              <div style="font-size:11px; opacity:0.85;">{detalhes}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )



