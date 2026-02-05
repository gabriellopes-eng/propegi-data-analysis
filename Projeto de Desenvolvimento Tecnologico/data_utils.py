import pandas as pd
import numpy as np
import itertools
from requests_github import (
    listar_backups_disponiveis,
    carregar_backup_json,
    carregar_todos_os_backups,
    obter_metadata_ultimo_backup,
    carregar_ultimo_backup_json,
)


# --- UTILITÁRIOS DE TRATAMENTO DE DADOS ---

BRL_COLS = [
    "valorPactuado",
    "valorAgencia",
    "valorUnidade",
    "valorIAUPE",
]

def _br_to_float(serie: pd.Series) -> pd.Series:
    """
    Converte '1.234.567,89' -> 1234567.89. Aceita também numérico.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    
    serie = serie.fillna("0").astype(str)
    serie = serie.str.strip()  # Remove espaços e caracteres invisíveis do início ao fim
    serie = serie.str.replace(r'[^\d\.\,]', '', regex=True)  # Remove qualquer coisa que não seja dígito, ponto ou vírgula

    # Conversão BR -> Float
    serie = serie.str.replace(".", "", regex=False)  # Remove separador de milhar (ponto)
    serie = serie.str.replace(",", ".", regex=False)  # Substitui vírgula por ponto decimal
    
    return pd.to_numeric(serie, errors="coerce").fillna(0.0)

def normalize_values(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que colunas monetárias estejam em float."""
    for c in BRL_COLS:
        if c in df.columns:
            df[c] = _br_to_float(df[c])
    return df

def prepare_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Converte 'dataPublicacao' e cria colunas Ano/Mes/MesNome."""
    df = df.copy()

    # Colunas de data a serem convertidas
    date_cols = ["dataPublicacao", "inicioData", "terminoData"]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["Ano"] = df["dataPublicacao"].dt.year
    df["Mes"] = df["dataPublicacao"].dt.month
    df["MesNome"] = df["dataPublicacao"].dt.strftime("%m/%b")
    return df

"""Extrai o ano do formato 'XXX-AAAA'."""
def _extract_agreement_year(agreement_series: pd.Series) -> pd.Series:
    serie = agreement_series.astype(str).str.split('-').str[-1]
    # Converte para numérico e coerce erros (onde a string não é um ano)
    return pd.to_numeric(serie, errors='coerce')

# Cria uma coluna 'AnoProjeto' usando lógica sequencial (Data Publicação > InícioData > Acordo).
def impute_project_date(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 1. Trata 'acordoConvenioNumero' para extrair o ano
    # O Ano será preenchido como NaN se a extração falhar.
    df['AnoAcordo'] = _extract_agreement_year(df['acordoConvenioNumero'])
    
    # 2. Preenche os NaNs em 'Ano' com o 'Ano' de 'InícioData' (se InícioData for válida)
    # df['InícioData'].dt.year obtém o ano do objeto datetime.
    df['Ano'] = df['Ano'].fillna(df['inicioData'].dt.year)
    
    # 3. Preenche os NaNs restantes em 'Ano' com o 'Ano' extraído do acordo
    df['Ano'] = df['Ano'].fillna(df['AnoAcordo'])
    
    # 4. Remove a coluna auxiliar e converte 'Ano' para inteiro (para visualização limpa)
    df = df.drop(columns=['AnoAcordo'], errors='ignore')
    
    # 5. Cria a categoria "Não Definido" para o agrupamento, onde o ano ainda é nulo.
    # Converte o Ano para string para poder usar 'Não Definido' na mesma coluna
    df['Ano'] = df['Ano'].fillna(9999).astype(int).astype(str).replace('9999', 'Não Definido')
    
    return df

def aggregate_monthly_data(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """
    Sums values by month (1..12) for the given year (Agency, Unit, IA-UPE).
    Ensures all 12 months are present, filling gaps with 0.0.
    """
    df_year = df[df["Ano"] == ano].copy()
    if df_year.empty:
        # If no data, just use the template and fill values with 0.0
        df_template = pd.DataFrame({"Mes": range(1, 13)})
        df_template["MesNome"] = df_template["Mes"].apply(lambda m: pd.Timestamp(year=ano, month=m, day=1).strftime("%m/%b"))
        for c in BRL_COLS:
            df_template[c] = 0.0
        return df_template

    # If data exists, group it
    df_grouped = (
        df_year.groupby(["Mes", "MesNome"], as_index=False)[BRL_COLS]
        .sum()
        .sort_values("Mes")
    )
    df_all_months = pd.DataFrame({"Mes": range(1, 13)})
    df_all_months["MesNome"] = df_all_months["Mes"].apply(
        lambda m: pd.Timestamp(year=ano, month=m, day=1).strftime("%m/%b")
    )
    out = df_all_months.merge(df_grouped, on=["Mes", "MesNome"], how="left").fillna(0.0)
    return out

# Calculates year totals (sum of months) for dashboard cards
def calculate_annual_kpis(df_monthly: pd.DataFrame) -> dict:
    return {
        "agencia": float(df_monthly["valorAgencia"].sum()) if "valorAgencia" in df_monthly else 0.0,
        "unidade": float(df_monthly["valorUnidade"].sum()) if "valorUnidade" in df_monthly else 0.0,
        "ia_upe": float(df_monthly["valorIAUPE"].sum()) if "valorIAUPE" in df_monthly else 0.0,
    }

# Formats float to simple BRL currency string (R$ 1.234,56).
def to_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def get_recent_agreements(df: pd.DataFrame) -> pd.DataFrame:
    # Returns the top 5 projects sorted by inicioData (descending)
    return (
        df.copy()
        .sort_values(by='inicioData', ascending=False)
        .head(5)
    )

# -------- QUARTER AND SEMESTER ANALYSIS (BEGIN) ----------

def aggregate_agreements_by_period(df: pd.DataFrame) -> pd.DataFrame:
    
    # Generate consolidated DataFrame for tabular display (Quarter, Semester, Year)
    df_temp = df.copy()

    # Safety check: Return empty if date column is missing or invalid
    if 'inicioData' not in df_temp.columns or not pd.api.types.is_datetime64_any_dtype(df_temp['inicioData']):
        print("Error: 'inicioData' column missing or invalid format.")
        return pd.DataFrame() 
    
    # Drop rows with missing essential values
    df_temp = df_temp.dropna(subset=['inicioData', 'nomeProjeto']).copy()

    if df_temp.empty:
        return pd.DataFrame()
    
    # Create time-based columns
    df_temp['Ano'] = df_temp['inicioData'].dt.year.astype(int)
    df_temp['Trimestre'] = df_temp['inicioData'].dt.quarter.astype(int).astype(str) + 'º Trimestre'
    df_temp['Semestre'] = np.where(df_temp['inicioData'].dt.month <= 6, '1º Semestre', '2º Semestre')

    years = sorted(df_temp['Ano'].unique())
    # Defines the exact order in the table
    period_hierarchy = [
        'Total Ano',
        '1º Semestre',
        '2º Semestre',
        '1º Trimestre',
        '2º Trimestre',
        '3º Trimestre',
        '4º Trimestre'
    ]

    # Função Agregadora
    def list_names(serie: pd.Series) -> str:
        names_list = serie.sort_values().astype(str).tolist()
        return '; '.join(names_list) if names_list else '-'

    # Aggregation Dictionary
    agg_dict = {'nomeProjeto': [('Qtd Acordos', 'count'), ('Nomes dos Projetos', list_names)]}
    frames = []

    # --- 1. QUARTERLY LEVEL ---
    quarters = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
    df_skeleton = pd.DataFrame(index=pd.MultiIndex.from_product([years, quarters], names=['Ano', 'Trimestre'])).reset_index()
    
    df_actual = df_temp.groupby(['Ano', 'Trimestre']).agg(agg_dict).reset_index()
    df_actual.columns = ['Ano', 'Trimestre', 'Qtd Acordos', 'Nomes dos Projetos']
    
    df_final_trim = pd.merge(df_skeleton, df_actual, on=['Ano', 'Trimestre'], how='left')

    # 1º Cria coluna auxiliar de Semestre (para agrupar/ordenar) e 2º Define o nome limpo na tabela
    df_final_trim['Semestre'] = np.where(df_final_trim['Trimestre'].str.startswith(('1','2')), '1º Semestre', '2º Semestre') # necessário para gráfico ou agrupar os dados
    df_final_trim['Período'] = df_final_trim['Trimestre']
    frames.append(df_final_trim)

    # --- 2. SEMESTER LEVEL ---
    semestres = ['1º Semestre', '2º Semestre']
    df_skeleton_sem = pd.DataFrame(index=pd.MultiIndex.from_product([years, semestres], names=['Ano', 'Semestre'])).reset_index()
    
    df_actual_sem = df_temp.groupby(['Ano', 'Semestre']).agg(agg_dict).reset_index()
    df_actual_sem.columns = ['Ano', 'Semestre', 'Qtd Acordos', 'Nomes dos Projetos']
    
    df_final_sem = pd.merge(df_skeleton_sem, df_actual_sem, on=['Ano', 'Semestre'], how='left')

    df_final_sem['Período'] = df_final_sem['Semestre']
    df_final_sem['Trimestre'] = '-'
    frames.append(df_final_sem)

   # --- 3. ANNUAL LEVEL ---
    df_year = df_temp.groupby(['Ano']).agg(agg_dict).reset_index()
    df_year.columns = ['Ano', 'Qtd Acordos', 'Nomes dos Projetos']
    df_year['Período'] = 'Total Ano'
    df_year['Semestre'] = '-'
    df_year['Trimestre'] = '-'
    frames.append(df_year)

    # Concatenate and sort
    df_final = pd.concat(frames, ignore_index=True)
    
    # Fill missing values
    df_final['Qtd Acordos'] = df_final['Qtd Acordos'].fillna(0).astype(int)
    df_final['Nomes dos Projetos'] = df_final['Nomes dos Projetos'].fillna('-')

    # Converts 'Period' to a Category with a defined order
    df_final['Período'] = pd.Categorical(
        df_final['Período'], 
        categories=period_hierarchy, 
        ordered=True
    )

    # Pandas automatically sorts based on the 'period_hierarchy' list
    df_final = df_final.sort_values(by=['Ano', 'Período'], ascending=[False, True])

    final_columns = ['Ano', 'Período', 'Semestre', 'Trimestre', 'Qtd Acordos', 'Nomes dos Projetos']
    
    return df_final[final_columns]

# -------- QUARTER AND SEMESTER ANALYSIS (END) ----------
