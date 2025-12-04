import streamlit as st
import plotly.express as px
import pandas as pd
from data_utils import (
    listar_backups_disponiveis,
    carregar_backup_json,
)
from analise_utils.recebimentos_mensais_utils import (
    preparar_datas,
    imputar_data_projeto,
    acordos_recentes,
    normalizar_valores,
    brl,
)

st.title("◈ Projetos em desenvolvimento por segmento e ano")
st.caption("Visualização da quantidade de projetos por segmento em cada ano.")

# Carregar o backup mais recente do GitHub
dados_backups = listar_backups_disponiveis()
backup_mais_recente = dados_backups[0]["nome_arquivo"]
df = carregar_backup_json(backup_mais_recente)
df = pd.DataFrame(df)
df = normalizar_valores(df)
df = preparar_datas(df)
df = imputar_data_projeto(df)

# Verifica se a coluna "segmento" existe
if "segmento" not in df.columns:
    st.error("A coluna 'segmento' não foi encontrada no JSON.")
    st.stop()

# Tratamento da coluna 'segmento'
if 'segmento' in df.columns:
    df['segmento'] = df['segmento'].fillna('Não Definido')

# Função para injetar CSS customizado
def _inject_css():
    st.markdown(
        """
        <style>
          .project-card {
            padding: 10px 10px;
            border-left: 5px solid #00BFFF;
            background: #1e1e1e;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            height: 100%;
          }
          .project-title {
            font-size: 1.0rem;
            font-weight: 600;
            color: #74CCF4;
            margin-bottom: 3px;
          }
          .project-detail {
            font-size: 0.8rem;
            color: #CCCCCC;
            margin-top: 2px;
            line-height: 1.3;
          }
          .project-value {
            font-size: 1.05rem;
            font-weight: 700;
            color: #4CAF50;
            margin-top: 8px;
            padding-top: 5px;
            border-top: 1px dashed rgba(255,255,255,0.1);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

def agreement_card(projeto, segmento, pactuado, inicio, termino, coordenador):
    inicio_str = inicio.strftime('%d/%m/%Y') if pd.notna(inicio) else "N/D"
    termino_str = termino.strftime('%d/%m/%Y') if pd.notna(termino) else "N/D"
    st.markdown(
        f"""
        <div class="project-card">
          <div class="project-title">{projeto}</div>
          <div class="project-detail">
            Segmento: <strong>{segmento}</strong>
          </div>
          <div class="project-detail">
            Coordenador: <strong>{coordenador}</strong>
          </div>
          <div style="margin-top: 10px;">
            Início: <span style="font-weight: 600;">{inicio_str}</span> |
            Término: <span style="font-weight: 600;">{termino_str}</span>
          </div>
          <div class="project-value" style="margin-top: 10px;">
            Valor Pactuado: {brl(pactuado)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

_inject_css()

st.subheader("Acordos Firmados Recentemente")
df_recentes = acordos_recentes(df)
num_cards = len(df_recentes)

if num_cards == 0:
    st.info("Nenhum acordo recente encontrado ou dados insuficientes.")
else:
    tab1, tab2, tab3 = st.tabs(["Pag 1", "Pag 2", "Pag 3"])
    with tab1:
        if num_cards >= 2:
            col1, col2 = st.columns(2)
            with col1:
                row0 = df_recentes.iloc[0]
                agreement_card(projeto=row0.get("nomeProjeto", "N/A"), segmento=row0.get("segmento", "N/A"), pactuado=row0.get("valorPactuado", 0.0), inicio=row0.get("inicioData"), termino=row0.get("terminoData"), coordenador=row0.get("coordenador", "N/A"))
            with col2:
                row1 = df_recentes.iloc[1]
                agreement_card(projeto=row1.get("nomeProjeto", "N/A"), segmento=row1.get("segmento", "N/A"), pactuado=row1.get("valorPactuado", 0.0), inicio=row1.get("inicioData"), termino=row1.get("terminoData"), coordenador=row1.get("coordenador", "N/A"))
        else:
            st.info(f"Apenas {num_cards} acordos disponíveis. Conteúdo da Pag 1 incompleto.")
    with tab2:
        if num_cards >= 4:
            col3, col4 = st.columns(2)
            with col3:
                row2 = df_recentes.iloc[2]
                agreement_card(projeto=row2.get("nomeProjeto", "N/A"), segmento=row2.get("segmento", "N/A"), pactuado=row2.get("valorPactuado", 0.0), inicio=row2.get("inicioData"), termino=row2.get("terminoData"), coordenador=row2.get("coordenador", "N/A"))
            with col4:
                row3 = df_recentes.iloc[3]
                agreement_card(projeto=row3.get("nomeProjeto", "N/A"), segmento=row3.get("segmento", "N/A"), pactuado=row3.get("valorPactuado", 0.0), inicio=row3.get("inicioData"), termino=row3.get("terminoData"), coordenador=row3.get("coordenador", "N/A"))
        elif num_cards > 2:
            st.info(f"Apenas {num_cards} acordos disponíveis. Conteúdo da Pag 2 incompleto.")
        else:
            st.info("Página 2 vazia. Mínimo de 3 acordos necessários.")
    with tab3:
        if num_cards == 5:
            col_side1, col_center, col_side2 = st.columns([1, 1.5, 1])
            with col_center:
                row4 = df_recentes.iloc[4]
                agreement_card(projeto=row4.get("nomeProjeto", "N/A"), segmento=row4.get("segmento", "N/A"), pactuado=row4.get("valorPactuado", 0.0), inicio=row4.get("inicioData"), termino=row4.get("terminoData"), coordenador=row4.get("coordenador", "N/A"))
        else:
            st.info("Página 3 vazia. Mínimo de 5 acordos necessários.")

st.markdown("---")

# Agrupamento: conta projetos por Ano e Segmento
df_group = (
    df.groupby(["Ano", "segmento"]).size().reset_index(name="QtdProjetos").sort_values(["Ano", "segmento"])
)

# Gráfico de barras empilhadas
fig = px.bar(
    df_group,
    x="Ano",
    y="QtdProjetos",
    color="segmento",
    text="QtdProjetos",
    title="❖ Projetos em desenvolvimento por segmento/ano",
    labels={"QtdProjetos": "Quantidade de Projetos"},
)
fig.update_layout(barmode="stack", xaxis=dict(type="category"))
st.plotly_chart(fig, use_container_width=True)

with st.expander("◆ Ver tabela agregada"):
    st.dataframe(df_group, use_container_width=True)

# VALIDAÇÃO DE CONTAGEM
st.subheader("Verificação de Integridade dos Dados")
total_df_original = len(df)
total_df_agregado = df_group["QtdProjetos"].sum()
col_original, col_agregado, col_status = st.columns(3)
col_original.metric("Total de Linhas (Original)", total_df_original)
col_agregado.metric("Total Agregado (Soma do Gráfico)", total_df_agregado)
if total_df_original == total_df_agregado:
    col_status.success("✅ Contagem validada! O gráfico inclui 100% dos projetos.")
else:
    col_status.error(f"❌ Erro de Contagem: Diferença de {total_df_original - total_df_agregado} projetos. Verifique filtros ou colunas com valores nulos.")
st.markdown("---")

# Relatório de Valores Nulos
st.subheader("Relatório de Valores Nulos")
nulos_e_imputados_ano = (
    df['Ano'].isna() | (df['Ano'] == 'Não Definido')
).sum()
nulos_e_imputados_segmento = (
    df['segmento'].isna() | (df['segmento'] == 'Não Definido')
).sum()
st.markdown(f"- Projetos sem **Ano** de Publicação: **{nulos_e_imputados_ano}**")
st.markdown(f"- Projetos sem **Segmento** definido: **{nulos_e_imputados_segmento}**")
