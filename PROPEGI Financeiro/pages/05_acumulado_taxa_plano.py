from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import carregar_dados, filtrar_por_ano

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Accumulated - Fee/Work Plan", layout="wide")

# Título principal da página
st.header("Analysis of the Complete Period by Fee and Work Plan", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
This analysis presents the accumulated values by type of fee and work plan over the entire period, providing a consolidated view of the main revenue sources and their evolution.
""")

# Carrega os dados da pasta de entrada
# Aqui, todos os arquivos JSON são carregados e combinados em um único DataFrame
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    # Exibe uma mensagem de erro e interrompe a execução se houver problemas ao carregar os dados
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Cria uma lista de anos disponíveis para o filtro
anos_disponiveis = sorted(df["ano"].unique().tolist())

# Interface para seleção de filtros
# Permite ao usuário filtrar os dados por ano
anos_sel = st.multiselect("Filter by Year (optional)", anos_disponiveis, default=anos_disponiveis)

# Aplica o filtro de ano selecionado pelo usuário
df_filtrado = filtrar_por_ano(df, anos_sel)

# Verifica se há dados após os filtros
if df_filtrado.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("No data available for the selected filters.")
    st.stop()

# Agrupa os dados por projeto e categoria do recurso
# Isso gera o total acumulado para cada projeto e categoria
acumulado_categoria = (
    df_filtrado.groupby(["nomeProjeto", "categoriaDoRecurso"], as_index=False)["valorFloat"]
    .sum()  # Soma os valores financeiros por projeto e categoria
    .rename(columns={"valorFloat": "Total"})  # Renomeia a coluna para "Total"
)

# Cria um gráfico de barras agrupadas usando Plotly Express
# O gráfico mostra os valores acumulados por projeto e categoria
fig = px.bar(
    acumulado_categoria,
    x="nomeProjeto",  # Nome do projeto no eixo X
    y="Total",  # Total financeiro no eixo Y
    color="categoriaDoRecurso",  # Agrupa as barras por categoria
    barmode="group",  # Define o modo de barras agrupadas
    text="Total",  # Exibe os valores diretamente nas barras
    labels={
        "nomeProjeto": "Projeto",
        "Total": "Valor (R$)",
        "categoriaDoRecurso": "Categoria"
    },
    color_discrete_map={  # Define as cores para cada categoria
        "Taxa": "#EF4444",               # Vermelho para "Taxa"
        "Plano de Trabalho": "#3B82F6"  # Azul para "Plano de Trabalho"
    }
)

# Personaliza o texto exibido no gráfico e o layout
fig.update_traces(
    texttemplate="R$ %{y:,.0f}",  # Formata os valores exibidos nas barras
    textposition="outside"  # Exibe os valores fora das barras
)
fig.update_layout(
    xaxis_title="Projeto",  # Título do eixo X
    yaxis_title="Valor Acumulado (R$)",  # Título do eixo Y
    yaxis_tickformat=",.0f",  # Formata os valores do eixo Y como moeda
    height=500,  # Define a altura do gráfico
    legend_title="Categoria",  # Título da legenda
    xaxis_tickangle=-45  # Inclina os rótulos do eixo X para melhor leitura
)

# Exibe o gráfico na página
st.plotly_chart(fig, width='stretch')

# Exibe uma tabela detalhada com os valores acumulados por projeto e categoria
# A tabela mostra os mesmos dados do gráfico, mas em formato tabular
st.subheader("Detailed Table - Accumulated Values")
tabela_pivot = acumulado_categoria.pivot_table(
    index="nomeProjeto",  # Índice da tabela: Nome do projeto
    columns="categoriaDoRecurso",  # Colunas: Categoria do recurso
    values="Total",  # Valores: Total financeiro
    fill_value=0  # Preenche valores ausentes com 0
)

# Adiciona uma coluna de total geral para cada projeto
tabela_pivot["Total Geral"] = tabela_pivot.sum(axis=1)

# Exibe a tabela com formatação de moeda
st.dataframe(
    tabela_pivot.style.format("R$ {:,.2f}"),  # Formata os valores como moeda
    width='stretch',
    height=400
)
