import streamlit as st
import plotly.express as px
import pandas as pd
from data_utils import listar_backups_disponiveis, carregar_backup_json
from analise_utils.recebimentos_mensais_utils import normalizar_valores, preparar_datas
from analise_utils.recebimentos_por_setor_utils import recebimentos_por_setor

def _brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _inject_css():
    st.markdown(
        """
        <style>
          .kpi-card {
            background: #111418;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 16px 18px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.25);
          }
          .kpi-title { font-size: 0.92rem; color: #c9d1d9; margin-bottom: 6px; }
          .kpi-big   { font-size: 1.75rem; font-weight: 700; margin-bottom: 8px; line-height: 1.2; }
          .kpi-small { font-size: 0.85rem; color: #9aa4af; }
          .kpi-small span { color: #c9d1d9; font-weight: 600; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def kpi_card(title: str, big_value: str, small_label: str, small_value: str):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">{title}</div>
          <div class="kpi-big">{big_value}</div>
          <div class="kpi-small"><span>{small_label}</span> {small_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.set_page_config(layout="wide")
st.title("◈ Recebimentos por setor (segmento)")
st.caption("Comparativo de quanto cada segmento/setor recebeu em cada ano.")

# Carregamento dos dados mais recentes do GitHub
dados_backups = listar_backups_disponiveis()
backup_mais_recente = dados_backups[0]["nome_arquivo"]
df = carregar_backup_json(backup_mais_recente)
df = pd.DataFrame(df)
df = normalizar_valores(df)
df = preparar_datas(df)

# Verifica se a coluna "segmento" existe
if "segmento" not in df.columns:
    st.error("A coluna 'segmento' não foi encontrada no JSON.")
    st.stop()

# Agrupamento por Ano e Segmento
df_group = recebimentos_por_setor(df)

# Gráfico
fig = px.bar(
    df_group,
    x="Ano",
    y=["valorAgencia", "valorUnidade", "valorIAUPE"],
    color="segmento",
    barmode="group",
    text_auto=".2s",
    title="❖ Recebimentos por setor (segmento)",
    labels={"value": "R$ total no ano", "variable": "Órgão", "segmento": "Setor"},
)
fig.update_layout(xaxis=dict(type="category"))
st.plotly_chart(fig, use_container_width=True)

# Cards resumo
_inject_css()
st.subheader("❖ Resumo dos setores")

# Tabela
st.markdown("---")
with st.expander("◆ Ver tabela agregada"):
    st.dataframe(df_group, use_container_width=True)
