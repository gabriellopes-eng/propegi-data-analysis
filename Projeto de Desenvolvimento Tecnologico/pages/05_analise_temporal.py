import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from data_utils import (
    carregar_ultimo_backup_json,
    normalize_values,
    prepare_dates,
    aggregate_agreements_by_period,
)

st.set_page_config(layout="wide")
st.header("Análise Temporal de Acordos", divider="blue")
st.info("""
**Storytelling:**
Esta análise temporal permite visualizar a distribuição dos acordos ao longo do tempo, identificando períodos de maior ou menor atividade. Com isso, é possível compreender ciclos, sazonalidades e impactos de eventos externos na dinâmica dos projetos.
""")


# 1. CARREGAMENTO E LIMPEZA (dinâmico)
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

# Verifica se há dados para trabalhar
if df.empty or 'inicioData' not in df.columns:
    st.error("Não há dados suficientes para gerar a análise temporal.")
    st.stop()

# -------------------------------------------------------------
# VISUALIZAÇÃO DO TREEMAP
# -------------------------------------------------------------
st.subheader("Mapa de Árvore (Treemap)")
st.caption("Distribuição hierárquica: Ano > Semestre > Trimestre")

df_aggregated = aggregate_agreements_by_period(df)

if df_aggregated is None or df_aggregated.empty:
    st.error("Não há dados suficientes para gerar a análise temporal.")
    st.stop()

# Filtra apenas as linhas de nível 'Trimestre' para o gráfico
df_treemap = df_aggregated[df_aggregated['Trimestre'].str.contains('Trimestre', na=False)].copy()

# Filtramos zeros ANTES de qualquer coisa para evitar o erro de divisão
# Se Qtd Acordos for 0, o peso é 0 e quebra o cálculo da cor no treemap.
df_treemap = df_treemap[df_treemap['Qtd Acordos'] > 0]

if not df_treemap.empty:
    # Preparação Hierárquica
    df_treemap['Total'] = 'Total Geral de Projetos'
    df_treemap['Ano'] = df_treemap['Ano'].astype(str)

    # Ordenação (Ano Decrescente / Período Crescente)
    df_treemap = df_treemap.sort_values(by=['Ano', 'Semestre', 'Trimestre'], ascending=[True, True, True])

    fig = px.treemap(
        df_treemap,
        path=['Total', 'Ano', 'Semestre', 'Trimestre'], # Hierarquia garantida
        values='Qtd Acordos', 
        color='Qtd Acordos', 
        color_continuous_scale='RdBu',
        title="Hierarquia de Acordos Firmados"
    )
    fig.update_traces(
        sort=False, # impede que o Plotly reordene os blocos do maior para o menor. Força a seguir a ordem cronológica do df.
        textinfo="label+value",
        # Tooltip mostra o valor REAL (Qtd Acordos)
        customdata=df_treemap['Qtd Acordos'],
        hovertemplate='<b>%{label}</b><br>Total de Acordos: %{value}<extra></extra>'
    )
    st.plotly_chart(fig, width='stretch')
else:
    st.info("Dados insuficientes para o gráfico.")

st.markdown("---")

# -------------------------------------------------------------
# TABELA DE DETALHAMENTO (Usando a função do data_utils)
# -------------------------------------------------------------
st.subheader("Tabela Detalhada por Período")

# Criação da tabela
df_table = aggregate_agreements_by_period(df)

if not df_table.empty:
    # Filtro Interativo
    available_years = sorted(df_table['Ano'].unique().tolist(), reverse=True)
    selected_year = st.selectbox("Filtrar por Ano:", ['Todos'] + available_years)

    if selected_year != 'Todos':
        df_table = df_table[df_table['Ano'] == selected_year]

    # Exibição da Tabela
    st.dataframe(
        df_table,
        column_config={
            "Ano": st.column_config.NumberColumn(format="%d"),
            "Período": st.column_config.TextColumn("Período"),
            "Qtd Acordos": st.column_config.NumberColumn("Qtd Acordos"),
            "Nomes dos Projetos": st.column_config.TextColumn(
                "Projetos Firmados",
                width="large",
                help="Lista de projetos neste período"
            ),
            # retira as colunas de semestre e trimestre da tabela
            "Semestre": None,
            "Trimestre": None
        },
        width='stretch',
        hide_index=True
    )
else:
    st.info("Nenhum dado encontrado para a tabela.")
