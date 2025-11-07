import streamlit as st
import plotly.express as px

from data_utils import (          # <- import ABSOLUTO
    carregar_json,
    preparar_datas,
    input_path,                   # <- resolve caminho dentro de input/
    DEFAULT_JSON_NAME,            # <- nome padrão do JSON
)

st.title("◈ Projetos em desenvolvimento por segmento e ano")
st.caption("Visualização da quantidade de projetos por segmento em cada ano.")

# Carregamento
df = carregar_json(input_path(DEFAULT_JSON_NAME))
df = preparar_datas(df)

# Verifica se a coluna "Segmento" existe
if "Segmento" not in df.columns:
    st.error("A coluna 'Segmento' não foi encontrada no JSON.")
    st.stop()

# Agrupamento: conta projetos por Ano e Segmento
df_group = (
    df.groupby(["Ano", "Segmento"]).size().reset_index(name="QtdProjetos").sort_values(["Ano", "Segmento"]) 
)

# Gráfico de barras empilhadas
fig = px.bar(
    df_group,
    x="Ano",
    y="QtdProjetos",
    color="Segmento",
    text="QtdProjetos",
    title="❖ Projetos em desenvolvimento por segmento/ano",
    labels={"QtdProjetos": "Quantidade de Projetos"},
)
fig.update_layout(barmode="stack", xaxis=dict(type="category"))
st.plotly_chart(fig, width='stretch')

# Tabela
with st.expander("◆ Ver tabela agregada"):
    st.dataframe(df_group, width='stretch')
