import streamlit as st
import plotly.express as px
import pandas as pd

from data_utils import (
  carregar_ultimo_backup_json,  # dinâmico!
  preparar_datas,
  imputar_data_projeto,
  acordos_recentes,
  brl,
  normalizar_valores,
)

st.header("Projetos em desenvolvimento por segmento e ano", divider="blue")
st.info("""
**Storytelling:**
Esta análise mostra a quantidade de projetos em desenvolvimento por segmento e ano. O objetivo é evidenciar quais segmentos concentram mais projetos ao longo do tempo, permitindo identificar áreas estratégicas, tendências de crescimento e oportunidades de diversificação.
""")
st.caption("Visualização da quantidade de projetos por segmento em cada ano.")


# Carregamento dinâmico
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


# Verifica se a coluna "segmento" existe
if "segmento" not in df.columns:
    st.error("A coluna 'segmento' não foi encontrada no JSON.")
    st.stop()

# -------------- ACORDOS RECENTES (INÍCIO) --------------

# Função para injetar CSS customizado
def _inject_css():
    st.markdown(
        """
        <style>
          .project-card {
          /* espaçamento interno */
            padding: 10px 10px; 
            border-left: 5px solid #00BFFF; 
            background: #1e1e1e;
            border-radius: 8px;
            margin-bottom: 15px; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            height: 100%;
          }
          /* Ajustes nas fontes */
          .project-title { 
            font-size: 1.0rem; 
            font-weight: 600; 
            color: #74CCF4; 
            margin-bottom: 3px;
          }
          /* Reduz a fonte dos detalhes (segmento, coordenador, datas) */
          .project-detail { 
            font-size: 0.8rem; 
            color: #CCCCCC; 
            margin-top: 2px; /* Reduz o espaçamento entre as linhas de detalhe */
            line-height: 1.3; /* Melhora a leitura do texto longo */
          }
          /* Destaque para o valor monetário */
          .project-value { 
            font-size: 1.05rem; 
            font-weight: 700; 
            color: #4CAF50; 
            margin-top: 8px;
            padding-top: 5px; /* Diminui o padding acima do valor */
            border-top: 1px dashed rgba(255,255,255,0.1); /* Separador visual */
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Função de Card Customizada para Acordos
def agreement_card(projeto, segmento, pactuado, inicio, termino, coordenador):
    
    # Formata datas para DD/MM/AAAA (necessário pois o row[data] é um objeto datetime)
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

# Injeção de CSS
_inject_css()


st.subheader("Acordos Firmados Recentemente")

df_recentes = acordos_recentes(df)
num_cards = len(df_recentes)

if num_cards == 0:
    st.info("Nenhum acordo recente encontrado ou dados insuficientes.")
else:
    # 1. Define as abas: Pag 1 (Cards 1 e 2), Pag 2 (Cards 3 e 4), Pag 3 (Card 5)
    tab1, tab2, tab3 = st.tabs(["Pag 1", "Pag 2", "Pag 3"])

    # --- TAB 1: Cards 1 e 2 ---
    with tab1:
        if num_cards >= 2:
            col1, col2 = st.columns(2)
            
            # Card 1 (Índice 0)
            with col1:
                row0 = df_recentes.iloc[0]
                agreement_card(projeto=row0.get("nomeProjeto", "N/A"), segmento=row0.get("segmento", "N/A"), pactuado=row0.get("valorPactuado", 0.0), inicio=row0.get("inicioData"), termino=row0.get("terminoData"), coordenador=row0.get("coordenador", "N/A"))
            
            # Card 2 (Índice 1)
            with col2:
                row1 = df_recentes.iloc[1]
                agreement_card(projeto=row1.get("nomeProjeto", "N/A"), segmento=row1.get("segmento", "N/A"), pactuado=row1.get("valorPactuado", 0.0), inicio=row1.get("inicioData"), termino=row1.get("terminoData"), coordenador=row1.get("coordenador", "N/A"))
        else:
            st.info(f"Apenas {num_cards} acordos disponíveis. Conteúdo da Pag 1 incompleto.")

    # --- TAB 2: Cards 3 e 4 ---
    with tab2:
        if num_cards >= 4:
            col3, col4 = st.columns(2)

            # Card 3 (Índice 2)
            with col3:
                row2 = df_recentes.iloc[2]
                agreement_card(projeto=row2.get("nomeProjeto", "N/A"), segmento=row2.get("Segmento", "N/A"), pactuado=row2.get("valorPactuado", 0.0), inicio=row2.get("inicioData"), termino=row2.get("terminoData"), coordenador=row2.get("coordenador", "N/A"))
            
            # Card 4 (Índice 3)
            with col4:
                row3 = df_recentes.iloc[3]
                agreement_card(projeto=row3.get("nomeProjeto", "N/A"), segmento=row3.get("Segmento", "N/A"), pactuado=row3.get("valorPactuado", 0.0), inicio=row3.get("inicioData"), termino=row3.get("terminoData"), coordenador=row3.get("coordenador", "N/A"))
        elif num_cards > 2:
             st.info(f"Apenas {num_cards} acordos disponíveis. Conteúdo da Pag 2 incompleto.")
        else:
            st.info("Página 2 vazia. Mínimo de 3 acordos necessários.")


    # --- TAB 3: Card 5 (Último Card) ---
    with tab3:
        if num_cards == 5:
            # Centraliza o card único na aba (1 card em 3 colunas, usando a coluna do meio)
            col_side1, col_center, col_side2 = st.columns([1, 1.5, 1]) 
            
            with col_center:
                row4 = df_recentes.iloc[4]
                agreement_card(projeto=row4.get("nomeProjeto", "N/A"), segmento=row4.get("segmento", "N/A"), pactuado=row4.get("valorPactuado", 0.0), inicio=row4.get("inicioData"), termino=row4.get("terminoData"), coordenador=row4.get("coordenador", "N/A"))
        else:
            st.info("Página 3 vazia. Mínimo de 5 acordos necessários.")

st.markdown("---")

# -------------- ACORDOS RECENTES (FIM) --------------

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
st.plotly_chart(fig, width='stretch')

# Tabela
with st.expander("Ver tabela agregada"):
    st.dataframe(df_group, width='stretch')

