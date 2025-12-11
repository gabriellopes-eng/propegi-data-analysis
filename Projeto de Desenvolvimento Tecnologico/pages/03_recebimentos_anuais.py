import streamlit as st
import plotly.express as px
import numpy as np  # (não é usado aqui, mas pode ficar se for usar depois)

from data_utils import (
    carregar_ultimo_backup_json,  # dinâmico!
    normalizar_valores,
    preparar_datas,
)

# ---------- Utils de exibição ----------
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

# ---------- Página ----------
st.set_page_config(layout="wide")
st.title("◈ Recebimentos anuais por órgão (Agência, Unidade, IA-UPE)")
st.info("""
**Storytelling:**
Esta análise apresenta o total de recebimentos anuais dos projetos, permitindo uma visão macro do desempenho financeiro ao longo dos anos. Com isso, é possível identificar anos de maior captação, oscilações e tendências de crescimento ou retração.
""")
st.caption("Comparativo de quanto cada órgão recebeu em cada ano.")

# Carregamento
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

# Agrupamento por Ano
df_group = (
    df.groupby("Ano")[["valorAgencia", "valorUnidade", "valorIAUPE"]]
      .sum()
      .reset_index()
      .sort_values("Ano")
)

# Gráfico
fig = px.bar(
    df_group,
    x="Ano",
    y=["valorAgencia", "valorUnidade", "valorIAUPE"],
    barmode="group",
    text_auto=".2s",
    title="❖ Recebimentos anuais por órgão",
    labels={"value": "R$ total no ano", "variable": "Órgão"},
)
fig.update_layout(xaxis=dict(type="category"))
st.plotly_chart(fig, width='stretch')

# Cards resumo
_inject_css()
st.subheader("❖ Resumo dos anos")

tot_agencia = float(df_group["valorAgencia"].sum())
tot_unidade = float(df_group["valorUnidade"].sum())
tot_iaupe   = float(df_group["valorIAUPE"].sum())

df_group["TotalAno"] = (
    df_group["valorAgencia"] + df_group["valorUnidade"] + df_group["valorIAUPE"]
)
idx_pico   = df_group["TotalAno"].idxmax()
ano_pico   = int(df_group.loc[idx_pico, "Ano"])
valor_pico = float(df_group.loc[idx_pico, "TotalAno"])

periodo_txt = f"{int(df_group['Ano'].min())}–{int(df_group['Ano'].max())}"

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total acumulado — Agência", _brl(tot_agencia), "Período completo:", periodo_txt)
with c2:
    kpi_card("Total acumulado — Unidade", _brl(tot_unidade), "Período completo:", periodo_txt)
with c3:
    kpi_card("Total acumulado — IA-UPE", _brl(tot_iaupe), "Período completo:", periodo_txt)
with c4:
    kpi_card(f"Ano pico — {ano_pico}", _brl(valor_pico), "Maior soma entre órgãos:", "Soma dos 3 valores")

# Tabela
st.markdown("---")
with st.expander("◆ Ver tabela agregada"):
    st.dataframe(df_group, width='stretch')
