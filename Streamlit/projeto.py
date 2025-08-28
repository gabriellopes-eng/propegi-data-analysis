import re
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Projetos de Desenvolvimento Tecnológico", layout="wide")
st.title("📊 Projetos de Desenvolvimento Tecnológico")

# Entrada dos Dados 
BASE = Path(__file__).resolve().parent
CSV_PATH  = (BASE / "../Projeto de Desenvolvimento Tecnologico/output/dados_tratados.csv").resolve()
XLSX_PATH = (BASE / "../Projeto de Desenvolvimento Tecnologico/output/Projetos de Desenvolvimento Tecnologico.xlsx").resolve()

def read_any(path: Path):
    if path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")

if XLSX_PATH.exists():
    df = read_any(XLSX_PATH)
elif CSV_PATH.exists():
    df = read_any(CSV_PATH)
else:
    st.error(
        "Arquivo de dados não encontrado.\n\n"
        f"Esperado em:\n- {XLSX_PATH}\n- {CSV_PATH}" #<-- Acho que nao sera necessario la pra frente
    )
    st.stop()

#  Mostrar a base completa (inteira) 
st.subheader("Amostra dos dados - Tabela Completa")
st.dataframe(df, use_container_width=True)

#  Preparação de colunas - Nomes que eu vou Trabalhar
COL_DATA   = "Data publicação"
COLS_VAL   = ["Valor agência", "Valor unidade", "Valor IA-UPE"]
COL_ANO    = "Ano do Projeto"
COL_SEG    = "Segmento"
COL_ID     = "Projeto_ID"
COL_STATUS = "Status"

#  datas
df[COL_DATA] = pd.to_datetime(df[COL_DATA], errors="coerce", dayfirst=True)

#  parser robusto de valores (R$ 10.500,30 -> 10500.30)
def parse_money_series(s: pd.Series) -> pd.Series:
    def _one(x):
        if pd.isna(x):
            return 0.0
        if isinstance(x, (int, float, np.integer, np.floating)):
            return float(x)
        t = str(x).strip()
        if t in ("", "-"):
            return 0.0
        t = t.replace("R$", "").replace("r$", "").replace(" ", "").replace("\u2212", "-")
        has_dot, has_comma = "." in t, "," in t
        if has_dot and has_comma:
            t = t.replace(".", "").replace(",", ".")   # 10.500,30 -> 10500.30
        elif has_comma:
            t = t.replace(",", ".")                    # 10500,30 -> 10500.30
        t = re.sub(r"[^0-9\.\-]", "", t)
        try:
            return float(t)
        except Exception:
            return 0.0
    return s.apply(_one).astype(float)

for c in COLS_VAL:
    if c in df.columns:
        df[c] = parse_money_series(df[c])

#  Ano do Projeto --> Preciso ficar atento se não variar, se nao eu uso o ano da Data publicação
df[COL_ANO] = pd.to_numeric(df[COL_ANO], errors="coerce").astype("Int64")
if df[COL_ANO].dropna().nunique() <= 1:
    df[COL_ANO] = df[COL_DATA].dt.year.astype("Int64")
    st.caption("ℹ️ 'Ano do Projeto' não varia na base — usando ano de **Data publicação** como fallback.")

#  Auxiliares mensais para a 1º Análise - Primeira Analise
df = df.dropna(subset=[COL_DATA]).copy()
df["_ano"] = df[COL_DATA].dt.year.astype(int)
df["_mes"] = df[COL_DATA].dt.to_period("M")
df["_mes_label"] = df["_mes"].dt.strftime("%b-%y").str.capitalize()

#  1º Análise -> — Linhas mensais - Analise Comparativo
st.sidebar.header("Comparativo Mensal")
anos = sorted(df["_ano"].unique().tolist())
ano_sel = st.sidebar.selectbox("Filtro do Ano", anos, index=len(anos)-1)

df_ano = df[df["_ano"] == int(ano_sel)]
mensal = (
    df_ano.groupby("_mes")[COLS_VAL].sum()
          .reset_index()
          .sort_values("_mes")
)
mensal["_mes_label"] = mensal["_mes"].dt.strftime("%b-%y").str.capitalize()

mensal_long = mensal.melt(
    id_vars=["_mes", "_mes_label"],
    value_vars=COLS_VAL,
    var_name="Tipo",
    value_name="Valor (R$)"
)

st.subheader(f"Comparativo mensal: Agência x Unidade x IA-UPE — {ano_sel}")
fig = px.line(mensal_long, x="_mes_label", y="Valor (R$)", color="Tipo", markers=True)
fig.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)", hovermode="x unified")
fig.update_yaxes(tickprefix="R$ ", separatethousands=True)
st.plotly_chart(fig, use_container_width=True)

# aviso se tudo zerar --> Manter por enquanto
if mensal[COLS_VAL].to_numpy().sum() == 0:
    st.warning("Os valores do ano selecionado somaram 0 após a conversão. "
               "Verifique as colunas de valor ou escolha outro ano.")

#  Cards 
def fmt_brl(x: float) -> str:
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown("### 📌 Resumo do ano")
if mensal.empty:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Média mensal — Agência", "R$ 0,00")
    with c2: st.metric("Média mensal — Unidade", "R$ 0,00")
    with c3: st.metric("Média mensal — IA-UPE", "R$ 0,00")
    with c4: st.metric("Pico do ano —", "R$ 0,00")
else:
    medias = mensal[COLS_VAL].mean()
    totais_mes = mensal[COLS_VAL].sum(axis=1)
    i_pico = int(totais_mes.idxmax())
    mes_pico_label = mensal.loc[i_pico, "_mes_label"]
    valor_pico = float(totais_mes.loc[i_pico])

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Média mensal — Agência", fmt_brl(medias["Valor agência"]))
    with c2: st.metric("Média mensal — Unidade", fmt_brl(medias["Valor unidade"]))
    with c3: st.metric("Média mensal — IA-UPE", fmt_brl(medias["Valor IA-UPE"]))
    with c4: st.metric(f"Pico do ano — {mes_pico_label}", fmt_brl(valor_pico))

#  2º Análise -> — Colunas empilhadas (Ano × Segmento) 
st.markdown("---")
st.subheader("📊 Projetos por Ano do Projeto e Segmento — Colunas Empilhadas")

#  Filtro de Status do Projetos por Ano do Projeto e Segmento  (Concluído, Em andamento, Aberto, etc.)
st.sidebar.header("Projetos por Ano do Projeto e Segmento ")
status_lista = sorted(df[COL_STATUS].dropna().astype(str).unique().tolist())
preferidos = [s for s in status_lista if s.lower() in ["concluído","concluido","em andamento","aberto"]]
default_status = preferidos if preferidos else status_lista
status_sel = st.sidebar.multiselect("Filtro - Status", status_lista, default=default_status)
if not status_sel:
    status_sel = status_lista

df_t2 = df[df[COL_STATUS].astype(str).isin(status_sel)].copy()
if df_t2.empty:
    st.warning("Nenhum projeto com os status selecionados.")

#  Agregação: conta projetos unicos por Ano × Segmento
base_t2 = (
    df_t2.dropna(subset=[COL_ANO, COL_SEG, COL_ID])
         .groupby([COL_ANO, COL_SEG])[COL_ID]
         .nunique()
         .reset_index(name="Projetos")
)

if base_t2.empty:
    st.info("Sem dados suficientes para montar o gráfico da Task 2.")
else:
    base_t2["Ano_str"] = base_t2[COL_ANO].astype(int).astype(str)
    anos_ordem = sorted(base_t2["Ano_str"].unique().tolist(), key=int)

    fig_stack = px.bar(
        base_t2,
        x="Ano_str", y="Projetos",
        color=COL_SEG,
        barmode="stack",
        text="Projetos",
        category_orders={"Ano_str": anos_ordem},
        title="Projetos por Ano do Projeto e Segmento"
    )
    fig_stack.update_layout(
        xaxis_title="Ano do Projeto",
        yaxis_title="Projetos",
        legend_title="Segmento",
        hovermode="x unified",
    )
    fig_stack.update_traces(textposition="inside")
    st.plotly_chart(fig_stack, use_container_width=True)



# 3º Análise -> Recebimentos anuais: Agência x Unidade x IA-UPE 

st.markdown("---")
st.subheader("📊 Recebimentos anuais: Agência x Unidade x IA-UPE")


# Agregação anual usando "Ano do Projeto" ---> OBS: Eu já tratei no início do script
anual = (
    df.dropna(subset=[COL_ANO])[ [COL_ANO] + COLS_VAL ]
      .groupby(COL_ANO, dropna=True)
      .sum()
      .reset_index()
      .sort_values(COL_ANO)
)

if anual.empty:
    st.info("Sem dados suficientes para a análise anual.")
else:
    # preparar dados em formato longo para o gráfico
    anual_long = anual.melt(
        id_vars=[COL_ANO],
        value_vars=COLS_VAL,
        var_name="Tipo",
        value_name="Valor (R$)"
    )
    anual_long["Ano_str"] = anual_long[COL_ANO].astype(int).astype(str)
    anos_ordem = sorted(anual_long["Ano_str"].unique().tolist(), key=int)

    # Gráfico de colunas AGRUPADAS 
    fig_t3 = px.bar(
        anual_long,
        x="Ano_str", y="Valor (R$)", color="Tipo",
        barmode="group",
        category_orders={"Ano_str": anos_ordem},
        title="Recebimentos por ano — Agência x Unidade x IA-UPE"
    )

    fig_t3.update_layout(xaxis_title="Ano do Projeto", yaxis_title="Valor (R$)", hovermode="x unified")
    fig_t3.update_yaxes(tickprefix="R$ ", separatethousands=True)
    
    st.plotly_chart(fig_t3, use_container_width=True)

    # Tabelinha de Resumo 
    with st.expander("📄 Ver tabela anual (Agência/Unidade/IA-UPE)"):
        st.dataframe(
            anual.set_index(COL_ANO),
            use_container_width=True
        )

