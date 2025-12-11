import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from data_utils import (
    carregar_ultimo_backup_json,  # dinâmico!
    normalizar_valores,
    preparar_datas,
    imputar_data_projeto,
    agregar_acordos_por_periodo
)



st.set_page_config(layout="wide")
st.title("◈ Análise Temporal de Acordos")

st.info("""
**Storytelling:**
Esta análise temporal permite visualizar a distribuição dos acordos ao longo do tempo, identificando períodos de maior ou menor atividade. Com isso, é possível compreender ciclos, sazonalidades e impactos de eventos externos na dinâmica dos projetos.
""")


# 1. CARREGAMENTO E LIMPEZA (dinâmico)
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
df = imputar_data_projeto(df)

# Verifica se há dados para trabalhar
if df.empty or 'inicioData' not in df.columns:
    st.error("Não há dados suficientes para gerar a análise temporal.")
    st.stop()

# -------------------------------------------------------------
# VISUALIZAÇÃO DO TREEMAP
# -------------------------------------------------------------
st.subheader("◈ Mapa de Árvore (Treemap)")
st.caption("◈ Distribuição hierárquica: Ano > Semestre > Trimestre")

# Criação de um DF exclusivo para o gráfico
# Isso garante que as colunas Semestre e Trimestre existam sem depender da tabela agregada
df_grafico = df.dropna(subset=['inicioData']).copy()
df_grafico['Ano'] = df_grafico['inicioData'].dt.year
df_grafico['Mes'] = df_grafico['inicioData'].dt.month
df_grafico['Semestre'] = np.where(df_grafico['Mes'] <= 6, '1º Semestre', '2º Semestre')
df_grafico['Trimestre'] = df_grafico['inicioData'].dt.quarter.astype(str) + 'º Trimestre'

# Agrupa para contagem
df_treemap = df_grafico.groupby(['Ano', 'Semestre', 'Trimestre']).size().reset_index(name='Qtd Acordos')

if not df_treemap.empty:
    fig = px.treemap(
        df_treemap,
        path=['Ano', 'Semestre', 'Trimestre'], # Hierarquia garantida
        values='Qtd Acordos',
        color='Qtd Acordos',
        color_continuous_scale='RdBu',
        title="Hierarquia de Acordos Firmados"
    )
    fig.update_traces(textinfo="label+value") # Mostra nome e valor
    st.plotly_chart(fig, width='stretch')
else:
    st.info("Dados insuficientes para o gráfico.")

st.markdown("---")

# -------------------------------------------------------------
# TABELA DE DETALHAMENTO (Usando a função do data_utils)
# -------------------------------------------------------------
st.subheader("◈ Tabela Detalhada por Período")

# Gera a tabela usando a função que simplificada no data_utils
df_tabela = agregar_acordos_por_periodo(df)

if not df_tabela.empty:
    # Filtro Interativo
    anos = sorted(df_tabela['Ano'].unique().tolist(), reverse=True)
    ano_filtro = st.selectbox("Filtrar Tabela por Ano:", ['Todos'] + anos)

    if ano_filtro != 'Todos':
        df_tabela = df_tabela[df_tabela['Ano'] == ano_filtro]

    # Exibição Limpa
    st.dataframe(
        df_tabela,
        column_config={
            "Ano": st.column_config.NumberColumn(format="%d"), # Remove vírgula de milhar do ano
            "Nomes dos Projetos": st.column_config.TextColumn(
                "Projetos Firmados",
                width="large",
                help="Lista de projetos (separados por ponto e vírgula)"
            )
        },
        width='stretch',
        hide_index=True
    )
else:
    st.info("Nenhum dado encontrado para a tabela.")
