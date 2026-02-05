import streamlit as st
import plotly.express as px

from data_utils import (
    carregar_ultimo_backup_json,
    normalize_values,
    prepare_dates,
    to_brl,
)

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
st.header("Recebimentos anuais por órgão (Agência, Unidade, IA-UPE)", divider="blue")
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
df = normalize_values(df)
df = prepare_dates(df)

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

agencia_totals = float(df_group["valorAgencia"].sum())
unidade_totals = float(df_group["valorUnidade"].sum())
iaupe_totals   = float(df_group["valorIAUPE"].sum())

df_group["TotalAno"] = (
    df_group["valorAgencia"] + df_group["valorUnidade"] + df_group["valorIAUPE"]
)
peak_idx = df_group["TotalAno"].idxmax()
peak_year = int(df_group.loc[peak_idx, "Ano"])
peak_value = float(df_group.loc[peak_idx, "TotalAno"])

period_str = f"{int(df_group['Ano'].min())}–{int(df_group['Ano'].max())}"

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total acumulado — Agência", to_brl(agencia_totals), "Período completo:", period_str)
with c2:
    kpi_card("Total acumulado — Unidade", to_brl(unidade_totals), "Período completo:", period_str)
with c3:
    kpi_card("Total acumulado — IA-UPE", to_brl(iaupe_totals), "Período completo:", period_str)
with c4:
    kpi_card(f"Ano pico — {peak_year}", to_brl(peak_value), "Maior soma entre órgãos:", "Soma dos 3 valores")

# Tabela
st.markdown("---")
with st.expander("Ver tabela agregada"):
    st.dataframe(df_group, width='stretch')
