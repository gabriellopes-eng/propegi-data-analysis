import streamlit as st
import plotly.express as px
import numpy as np

from data_utils import (
    carregar_ultimo_backup_json,  # dinâmico!
    normalizar_valores,
    preparar_datas,
    agrupar_mensal,
    calculate_annual_kpis,
)

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

# -------- Página principal --------
st.header("Recebimentos mensais por órgão (Agência, Unidade, IA-UPE)", divider="blue")
st.info("""
**Storytelling:**
Esta análise apresenta a evolução dos recebimentos mensais dos projetos de desenvolvimento tecnológico. O objetivo é identificar padrões sazonais, tendências de crescimento ou queda ao longo do tempo, e fornecer subsídios para o planejamento financeiro e estratégico dos projetos.
""")

# Carregar e preparar dados (backup dinâmico)
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

# Filtro de ano
anos_disponiveis = sorted([int(a) for a in df["Ano"].dropna().unique()])
ano_sel = st.selectbox("Selecione o ano", anos_disponiveis, index=0)

# Agregação mensal (12 meses garantidos)
df_monthly = agrupar_mensal(df, ano_sel)

# Gráfico de linhas (3 séries)
fig = px.line(
    df_monthly,
    x="MesNome",
    y=["valorAgencia", "valorUnidade", "valorIAUPE"],
    markers=True,
    title=f"Recebimentos mensais — {ano_sel}",
    labels={"value": "R$ no mês", "MesNome": "Mês", "variable": "Órgão"},
)
fig.update_layout(legend_title_text="Órgão", xaxis_tickangle=-45)
st.plotly_chart(fig, width='stretch')

# Resumo do ano: MÉDIA + TOTAL + PICO 
_inject_css()
st.subheader("❖ Resumo do Ano")

# Totais anuais 
totais = calculate_annual_kpis(df_monthly)
tot_agencia = totais["agencia"]
tot_unidade = totais["unidade"]
tot_iaupe   = totais["ia_upe"]

# Médias mensais
media_agencia = float(np.mean(df_monthly["valorAgencia"]))
media_unidade = float(np.mean(df_monthly["valorUnidade"]))
media_iaupe   = float(np.mean(df_monthly["valorIAUPE"]))

# Pico do ano
df_monthly["TotalMes"] = df_monthly["valorAgencia"] + df_monthly["valorUnidade"] + df_monthly["valorIAUPE"]
idx_pico   = df_monthly["TotalMes"].idxmax()
mes_pico   = df_monthly.loc[idx_pico, "MesNome"]
valor_pico = float(df_monthly.loc[idx_pico, "TotalMes"])

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Média mensal — Agência", _brl(media_agencia), "Total anual — Agência:", _brl(tot_agencia))
with c2:
    kpi_card("Média mensal — Unidade", _brl(media_unidade), "Total anual — Unidade:", _brl(tot_unidade))
with c3:
    kpi_card("Média mensal — IA-UPE", _brl(media_iaupe), "Total anual — IA-UPE:", _brl(tot_iaupe))
with c4:
    kpi_card(f"Pico do ano — {mes_pico}", _brl(valor_pico), "Mês com maior soma:", "Soma dos 3 valores")

# Tabela 
st.markdown("---")
with st.expander("Ver tabela mensal detalhada"):
    st.dataframe(
        df_monthly[["Mes", "MesNome", "valorAgencia", "valorUnidade", "valorIAUPE", "TotalMes"]]
        .rename(columns={"MesNome": "Mês"}),
        width='stretch',
    )
