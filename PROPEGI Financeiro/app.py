import streamlit as st
from pathlib import Path

st.set_page_config(page_title="PROPEGI Financeiro - Modelo",page_icon="◈",layout="wide")

st.title("◈ PROPEGI Financeiro - Modelo")

st.markdown("---")
    
st.page_link("app.py", label="Home", icon="🏠")
st.page_link("pages/01_heatmap_comparativo.py", label="Análise 1 — Comparativo (Heatmap)", icon="1️⃣")
st.page_link("pages/02_somatorio_projetos.py", label="Análise 2 — Somatório por Projeto", icon="2️⃣")
st.page_link("pages/03_evolucao_mensal.py", label="Análise 3 — Total Mensal", icon="3️⃣")
st.page_link("pages/04_analise_mensal_taxa_plano.py", label="Análise 4 — Mensal Taxa Plano", icon="4️⃣")
st.page_link("pages/05_acumulado_taxa_plano.py", label="Análise 5 — Período Taxa Plano", icon="5️⃣")

    
# serve para verificar se o arquivo de dados existe
caminho_json = Path(__file__).parent / "input" / "dados.json"   
if caminho_json.exists():
    st.success(f"✅ Arquivo de dados encontrado: `{caminho_json.name}`")
else:
    st.error(f"❌ Arquivo de dados não encontrado em: `input/dados.json`")
