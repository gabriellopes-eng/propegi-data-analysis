import streamlit as st
import plotly.express as px
import pandas as pd
from data_utils import listar_backups_disponiveis, carregar_backup_json
from analise_utils.recebimentos_anuais_utils import agrupar_recebimentos_anuais, totais_acumulados, ano_pico
from analise_utils.recebimentos_mensais_utils import normalizar_valores, preparar_datas

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
st.title("◈ Recebimentos anuais por órgão (Agência, Unidade, IA-UPE)")
st.markdown(
    """
**Visão Executiva:**

Este quadro compara os recebimentos anuais entre Agência, Unidade e IA-UPE, destacando o desempenho financeiro de cada órgão ao longo dos anos. A análise facilita a identificação de padrões de crescimento, anos de pico e períodos de maior aporte financeiro. Com KPIs e gráficos comparativos, a gestão obtém uma visão consolidada dos resultados, podendo avaliar a efetividade das estratégias adotadas, justificar investimentos e planejar ações futuras com base em evidências concretas.
    """
)
st.caption("Comparativo de quanto cada órgão recebeu em cada ano.")

# Carregamento dos dados mais recentes do GitHub
dados_backups = listar_backups_disponiveis()
backup_mais_recente = dados_backups[0]["nome_arquivo"]
df = carregar_backup_json(backup_mais_recente)
df = pd.DataFrame(df)
df = normalizar_valores(df)
df = preparar_datas(df)

df_group = agrupar_recebimentos_anuais(df)

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
st.plotly_chart(fig, use_container_width=True)

# Cards resumo
_inject_css()
st.subheader("❖ Resumo dos anos")
totais = totais_acumulados(df_group)
ano_pico_val, valor_pico = ano_pico(df_group)
periodo_txt = f"{int(df_group['Ano'].min())}–{int(df_group['Ano'].max())}"

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total acumulado — Agência", _brl(totais["agencia"]), "Período completo:", periodo_txt)
with c2:
    kpi_card("Total acumulado — Unidade", _brl(totais["unidade"]), "Período completo:", periodo_txt)
with c3:
    kpi_card("Total acumulado — IA-UPE", _brl(totais["iaupe"]), "Período completo:", periodo_txt)
with c4:
    kpi_card(f"Ano pico — {ano_pico_val}", _brl(valor_pico), "Maior soma entre órgãos:", "Soma dos 3 valores")

# Tabela
st.markdown("---")
with st.expander("◆ Ver tabela agregada"):
    st.dataframe(df_group, use_container_width=True)
