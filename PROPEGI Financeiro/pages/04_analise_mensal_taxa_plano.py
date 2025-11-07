import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Permitir import do módulo raiz
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data_utils import carregar_financas_json, filtrar, validar_financas_df  # noqa: E402

CAMINHO_PADRAO_JSON = Path(__file__).resolve().parents[1] / "input" / "Financas.json"

st.set_page_config(page_title="Análise Mensal — Taxa/Plano", layout="wide", initial_sidebar_state="collapsed")

# Eu testando o estilo dos cards KPI 
st.markdown(
    """
    <style>
    .kpi-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 8px;
      padding: 20px;
      color: white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-title {
      font-size: 14px;
      opacity: 0.9;
      margin-bottom: 8px;
    }
    .kpi-big {
      font-size: 32px;
      font-weight: bold;
      margin: 10px 0;
    }
    .kpi-small {
      font-size: 12px;
      opacity: 0.8;
      margin-top: 10px;
    }
    .kpi-small span {
      opacity: 0.7;
    }
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

# Ordenacao temporal
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

st.subheader("Mensal por taxa")
st.plotly_chart(grafico_empilhado(df_filt, "Taxa", "Somatório mensal por taxa"), width='stretch')
st.subheader("Mensal por plano de trabalho")
st.plotly_chart(grafico_empilhado(df_filt, "Plano de Trabalho", "Somatório mensal por plano de trabalho"), width='stretch')

st.subheader("◆ Tabela mensal — Taxa × Plano de Trabalho")
tabela = (
    df_filt.groupby(["AnoMes", "ord_col", "Taxa", "Plano de Trabalho"], as_index=False)["Valor da folha"].sum()
    .rename(columns={"Valor da folha": "Total"})
    .sort_values(["ord_col", "Taxa", "Plano de Trabalho"])
)
st.dataframe(tabela[["AnoMes", "Taxa", "Plano de Trabalho", "Total"]].style.format({"Total": "{:,.2f}"}), width='stretch', height=450)

# Seção: 5 Acordos Mais Recentes
st.divider()
st.subheader("📋 Últimos 5 Acordos Firmados")

# Buscar os 5 registros mais recentes do DataFrame ORIGINAL completo (sem filtros)
df_completo = df.copy()
ultimos_5 = df_completo.sort_values("ord_col", ascending=False).head(5)

# Criar cards em colunas (5 cards lado a lado)
cols = st.columns(5)

for idx, (_, row) in enumerate(ultimos_5.iterrows()):
    with cols[idx]:
        # Pegar valores diretamente
        valor = float(row['Valor da folha']) if row['Valor da folha'] else 0.0
        sei = str(row.get('SEI', 'N/A'))
        taxa = str(row.get('Taxa', 'N/A'))
        plano = str(row.get('Plano de Trabalho', 'N/A'))
        status = str(row.get('Status', 'N/A'))
        projeto_nome = str(row['Projetos'])[:25] + "..." if len(str(row['Projetos'])) > 25 else str(row['Projetos'])
        
        # Formatar detalhes
        detalhes = f"Taxa: {taxa} | Plano: {plano} | Status: {status} | SEI: {sei}"
        
        kpi_card(
            title=f"📅 {row['AnoMes']}",
            big_value=f"R$ {valor:,.2f}",
            small_label=projeto_nome,
            small_value=detalhes
        )






