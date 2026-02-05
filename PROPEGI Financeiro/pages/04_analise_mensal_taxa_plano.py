from pathlib import Path
import streamlit as st
import plotly.express as px

# Importa funções utilitárias para carregar e filtrar os dados
from data_utils import carregar_dados, filtrar_por_ano

# Define o caminho da pasta de entrada onde os arquivos JSON estão armazenados
PASTA_INPUT = Path(__file__).resolve().parents[1] / "input"

# Configuração inicial da página
# Define o título da aba do navegador e o layout como "wide" (tela cheia)
st.set_page_config(page_title="Análise Mensal - Taxa/Plano", layout="wide")

# Título principal da página
st.header("Análise Mensal por Taxa e Plano de Trabalho", divider="blue")

# Descrição da análise para o usuário
st.info("""
**Storytelling:**
Esta análise detalha a evolução mensal dos valores por tipo de taxa e plano de trabalho, permitindo identificar a contribuição de cada categoria ao longo do tempo e apoiar decisões de gestão financeira.
""")

# Carrega os dados da pasta de entrada
# Aqui, todos os arquivos JSON são carregados e combinados em um único DataFrame
try:
    df = carregar_dados(PASTA_INPUT)
except Exception as e:
    # Exibe uma mensagem de erro e interrompe a execução se houver problemas ao carregar os dados
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Cria listas de opções para os filtros baseados nos dados carregados
anos_disponiveis = sorted(df["ano"].unique().tolist())  # Lista de anos únicos
projetos_disponiveis = sorted(df["nomeProjeto"].unique().tolist())  # Lista de projetos únicos

# Interface para seleção de filtros
# Permite ao usuário filtrar os dados por ano e selecionar um projeto específico
col1, col2 = st.columns(2)
with col1:
    anos_sel = st.multiselect("Filtrar por Ano", anos_disponiveis, default=anos_disponiveis)
with col2:
    projeto_sel = st.selectbox("Selecionar Projeto", projetos_disponiveis)

# Aplica os filtros selecionados pelo usuário
df_filtrado = filtrar_por_ano(df, anos_sel)  # Filtra pelos anos selecionados
df_filtrado = df_filtrado[df_filtrado["nomeProjeto"] == projeto_sel]  # Filtra pelo projeto selecionado

# Verifica se há dados após os filtros
if df_filtrado.empty:
    # Exibe um aviso e interrompe a execução se não houver dados para os filtros escolhidos
    st.warning("Sem dados para os filtros escolhidos.")
    st.stop()

# Agrupa os dados por mês e categoria do recurso
# Isso gera o total financeiro mensal para cada categoria (ex.: Taxa, Plano de Trabalho)
mensal_categoria = (
    df_filtrado.groupby(["mes", "numeroMes", "categoriaDoRecurso"], as_index=False)["valorFloat"]
    .sum()  # Soma os valores financeiros por mês e categoria
    .rename(columns={"valorFloat": "Total"})  # Renomeia a coluna para "Total"
    .sort_values("numeroMes")  # Ordena os dados pelo número do mês
)

# Cria um gráfico de barras agrupadas usando Plotly Express
# O gráfico mostra os valores financeiros por mês e categoria
fig = px.bar(
    mensal_categoria,
    x="mes",  # Mês no eixo X
    y="Total",  # Total financeiro no eixo Y
    color="categoriaDoRecurso",  # Agrupa as barras por categoria
    barmode="group",  # Define o modo de barras agrupadas
    text="Total",  # Exibe os valores diretamente nas barras
    labels={
        "mes": "Mês",
        "Total": "Valor (R$)",
        "categoriaDoRecurso": "Categoria"
    },
    color_discrete_map={  # Define as cores para cada categoria
        "Taxa": "#EF4444",               # Vermelho para "Taxa"
        "Plano de Trabalho": "#3B82F6"  # Azul para "Plano de Trabalho"
    },
    category_orders={  # Ordena os meses na ordem cronológica
        "mes": df_filtrado.sort_values("numeroMes")["mes"].unique().tolist()
    }
)

# Personaliza o texto exibido no gráfico e o layout
fig.update_traces(
    texttemplate="R$ %{y:,.0f}",  # Formata os valores exibidos nas barras
    textposition="outside"  # Exibe os valores fora das barras
)
fig.update_layout(
    xaxis_title="Mês",  # Título do eixo X
    yaxis_title="Valor (R$)",  # Título do eixo Y
    yaxis_tickformat=",.0f",  # Formata os valores do eixo Y como moeda
    height=500,  # Define a altura do gráfico
    legend_title="Categoria"  # Título da legenda
)

# Exibe o gráfico na página
st.plotly_chart(fig, width='stretch')

# Exibe uma tabela detalhada com os valores por mês e categoria
# A tabela mostra os mesmos dados do gráfico, mas em formato tabular
st.subheader("Tabela Detalhada")
tabela_pivot = mensal_categoria.pivot_table(
    index="mes",  # Índice da tabela: Mês
    columns="categoriaDoRecurso",  # Colunas: Categoria do recurso
    values="Total",  # Valores: Total financeiro
    fill_value=0  # Preenche valores ausentes com 0
).reindex(df_filtrado.sort_values("numeroMes")["mes"].unique())  # Ordena os meses na ordem cronológica

# Exibe a tabela com formatação de moeda
st.dataframe(
    tabela_pivot.style.format("R$ {:,.2f}"),  # Formata os valores como moeda
    width='stretch',
    height=400
)