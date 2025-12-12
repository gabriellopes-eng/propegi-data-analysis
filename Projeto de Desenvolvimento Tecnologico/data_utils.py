from __future__ import annotations
import re
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import requests
import numpy as np
import itertools

# --- CONFIGURAÇÕES GITHUB ---
URL_CONTEUDOS_GITHUB = "https://api.github.com/repos/propegi-upe/projects-automations/contents/automation/data/backups/technological-development"
PADRAO_BACKUP = r"backup-(\d{4}-\d{2}-\d{2})\.json$"

def extrair_data_do_nome(nome_arquivo: str) -> date | None:
    m = re.match(PADRAO_BACKUP, nome_arquivo)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except Exception:
            return None
    return None

def listar_backups_disponiveis() -> list:
    """
    Lista todos os arquivos de backup JSON disponíveis no GitHub.
    Retorna uma lista de dicionários com nome_arquivo, data_backup, download_url.
    """
    try:
        resposta = requests.get(URL_CONTEUDOS_GITHUB)
        resposta.raise_for_status()
        arquivos = resposta.json()
        backups = []
        for arq in arquivos:
            nome = arq.get("name", "")
            if nome.endswith(".json"):
                data = extrair_data_do_nome(nome)
                url = arq.get("download_url")
                if data and url:
                    backups.append({
                        "nome_arquivo": nome,
                        "data_backup": data,
                        "download_url": url
                    })
        if not backups:
            raise RuntimeError("Nenhum arquivo de backup JSON encontrado no GitHub!")
        backups.sort(key=lambda x: x["data_backup"], reverse=True)
        return backups
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao buscar backups no GitHub: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao processar arquivos de backup: {e}")

def carregar_backup_json(nome_arquivo: str) -> list:
    """
    Carrega o conteúdo de um backup JSON específico pelo nome do arquivo.
    Retorna uma lista de projetos.
    """
    try:
        backups = listar_backups_disponiveis()
        backup = next((b for b in backups if b["nome_arquivo"] == nome_arquivo), None)
        if not backup:
            raise RuntimeError(f"Backup '{nome_arquivo}' não encontrado na lista de backups disponíveis!")
        url = backup["download_url"]
        resposta = requests.get(url)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao baixar o backup JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar o backup JSON: {e}")

def carregar_todos_os_backups() -> dict:
    """
    Carrega todos os backups disponíveis e retorna um dicionário:
    { nome_arquivo: [lista de projetos], ... }
    """
    try:
        backups = listar_backups_disponiveis()
        todos = {}
        for b in backups:
            nome = b["nome_arquivo"]
            url = b["download_url"]
            try:
                resposta = requests.get(url)
                resposta.raise_for_status()
                todos[nome] = resposta.json()
            except Exception as e:
                todos[nome] = f"Erro ao baixar: {e}"
        return todos
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar todos os backups: {e}")

def obter_metadata_ultimo_backup() -> dict:
    """
    Busca o arquivo de backup JSON mais recente no GitHub e retorna seu metadata (inclui download_url).
    """
    try:
        resposta = requests.get(URL_CONTEUDOS_GITHUB)
        resposta.raise_for_status()
        arquivos = resposta.json()
        backups = []
        for arq in arquivos:
            nome = arq.get("name", "")
            if nome.endswith(".json"):
                data = extrair_data_do_nome(nome)
                if data:
                    backups.append((data, arq))
        if not backups:
            raise RuntimeError("Nenhum arquivo de backup JSON encontrado no GitHub!")
        backups.sort(reverse=True)
        return backups[0][1]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao buscar backups no GitHub: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao processar arquivos de backup: {e}")

def carregar_ultimo_backup_json() -> dict | list:
    """
    Baixa e retorna o conteúdo do último backup JSON do GitHub como dict/list.
    """
    try:
        metadata = obter_metadata_ultimo_backup()
        url = metadata.get("download_url")
        if not url:
            raise RuntimeError("Campo 'download_url' não encontrado no metadata do backup!")
        resposta = requests.get(url)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao baixar o backup JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar o backup JSON: {e}")
# --- FIM CONFIGURAÇÕES GITHUB ---









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
    serie = serie.str.strip() # remove espaços e caracteres invisíveis do início ao fim
    serie = serie.str.replace(r'[^\d\.\,]', '', regex=True) # Remove qualquer coisa que não seja dígito, ponto ou vírgula

    # Cconversão BR -> Float
    serie = (
        serie.str.replace(".", "", regex=False)  # Remove separador de milhar (ponto)
             .str.replace(",", ".", regex=False) # Substitui vírgula por ponto decimal
    )
    
    return pd.to_numeric(serie, errors="coerce").fillna(0.0)

def normalizar_valores(df: pd.DataFrame) -> pd.DataFrame:
    """Garante que colunas monetárias estejam em float."""
    for c in BRL_COLS:
        if c in df.columns:
            df[c] = _br_to_float(df[c])
    return df

def preparar_datas(df: pd.DataFrame) -> pd.DataFrame:
    """Converte 'dataPublicacao' e cria colunas Ano/Mes/MesNome."""
    df = df.copy()

    # Colunas de data a serem convertidas
    date_cols = ["dataPublicacao", "inicioData", "terminoData"]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    #df["dataPublicacao"] = pd.to_datetime(df["dataPublicacao"], errors="coerce") # verificar se não é uma redundância
    df["Ano"] = df["dataPublicacao"].dt.year
    df["Mes"] = df["dataPublicacao"].dt.month
    df["MesNome"] = df["dataPublicacao"].dt.strftime("%m/%b")
    return df

"""Extrai o ano do formato 'XXX-AAAA'."""
def _extrair_ano_do_acordo(serie_acordo: pd.Series) -> pd.Series:
    serie = serie_acordo.astype(str).str.split('-').str[-1]
    # Converte para numérico e coerce erros (onde a string não é um ano)
    return pd.to_numeric(serie, errors='coerce')

# Cria uma coluna 'AnoProjeto' usando lógica sequencial (Data Publicação > InícioData > Acordo).
def imputar_data_projeto(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # 1. Trata 'acordoConvenioNumero' para extrair o ano
    # O Ano será preenchido como NaN se a extração falhar.
    df['AnoAcordo'] = _extrair_ano_do_acordo(df['acordoConvenioNumero'])
    
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

def agrupar_mensal(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Soma por mês (1..12) os valores da agência, unidade e IA-UPE para o ano dado."""
    df_ano = df[df["Ano"] == ano].copy()
    if df_ano.empty:
        base = pd.DataFrame({"Mes": range(1, 13)})
        base["MesNome"] = base["Mes"].apply(lambda m: pd.Timestamp(year=ano, month=m, day=1).strftime("%m/%b"))
        for c in BRL_COLS:
            base[c] = 0.0
        return base

    grp = (
        df_ano.groupby(["Mes", "MesNome"], as_index=False)[BRL_COLS]
        .sum()
        .sort_values("Mes")
    )
    meses_completos = pd.DataFrame({"Mes": range(1, 13)})
    meses_completos["MesNome"] = meses_completos["Mes"].apply(
        lambda m: pd.Timestamp(year=ano, month=m, day=1).strftime("%m/%b")
    )
    out = meses_completos.merge(grp, on=["Mes", "MesNome"], how="left").fillna(0.0)
    return out

def kpis_anuais(df_mes: pd.DataFrame) -> dict:
    """Totais do ano (soma dos meses) para cards."""
    return {
        "agencia": float(df_mes["valorAgencia"].sum()) if "valorAgencia" in df_mes else 0.0,
        "unidade": float(df_mes["valorUnidade"].sum()) if "valorUnidade" in df_mes else 0.0,
        "ia_upe": float(df_mes["valorIAUPE"].sum()) if "valorIAUPE" in df_mes else 0.0,
    }

def brl(v: float) -> str:
    """Formata float para BRL simples (R$ 1.234,56)."""
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"
    
# Função para filtrar, ordenar e retornar os 5 projetos mais recentes
def acordos_recentes(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    # Ordena por InícioData em ordem decrescente (mais recentes primeiro)
    df_ordenado = df_copy.sort_values(by='inicioData', ascending=False)
    
    # Retorna os últimos 5
    return df_ordenado.head(5)

# --------- UTILITÁRIOS PARA TRATAMENTO DE DADOS ----------









# -------- ANALISE PARA TRIMESTRE E SEMESTRE (INÍCIO) ----------

def agregar_acordos_por_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera um DataFrame consolidado para exibição em TABELA (Trimestre, Semestre e Ano).
    """
    df_temp = df.copy()

    # Validação básica
    if 'inicioData' not in df_temp.columns or not pd.api.types.is_datetime64_any_dtype(df_temp['inicioData']):
        return pd.DataFrame() 
    
    # Remove nulos essenciais
    df_temp = df_temp.dropna(subset=['inicioData', 'nomeProjeto']).copy()

    if df_temp.empty:
        return pd.DataFrame()
    
    # Criação de colunas temporais
    df_temp['Ano'] = df_temp['inicioData'].dt.year.astype(int)
    df_temp['Trimestre'] = df_temp['inicioData'].dt.quarter.astype(int).astype(str) + 'º Trimestre'
    df_temp['Semestre'] = np.where(df_temp['inicioData'].dt.month <= 6, '1º Semestre', '2º Semestre')

    anos = sorted(df_temp['Ano'].unique())
    # Definimos aqui a ORDEM EXATA que queremos na tela
    ordem_periodos = [
        'Total Ano',
        '1º Semestre',
        '1º Trimestre (1º Semestre)',
        '2º Trimestre (1º Semestre)',
        '2º Semestre',
        '3º Trimestre (2º Semestre)',
        '4º Trimestre (2º Semestre)'
    ]

    # Função Agregadora
    def listar_nomes(serie: pd.Series) -> str:
        l = serie.sort_values().astype(str).tolist()
        return '; '.join(l) if l else '-'

    # Dicionário de Agregação
    agg_dict = {'nomeProjeto': [('Qtd Acordos', 'count'), ('Nomes dos Projetos', listar_nomes)]}
    resultados = []

    # --- 1. NÍVEL TRIMESTRAL ---
    trimestres = ['1º Trimestre', '2º Trimestre', '3º Trimestre', '4º Trimestre']
    df_rascunho = pd.DataFrame(index=pd.MultiIndex.from_product([anos, trimestres], names=['Ano', 'Trimestre'])).reset_index()
    
    df_real = df_temp.groupby(['Ano', 'Trimestre']).agg(agg_dict).reset_index()
    df_real.columns = ['Ano', 'Trimestre', 'Qtd Acordos', 'Nomes dos Projetos']
    
    df_final_trim = pd.merge(df_rascunho, df_real, on=['Ano', 'Trimestre'], how='left')

    # Formata o nome
    df_final_trim['Semestre'] = np.where(df_final_trim['Trimestre'].str.startswith(('1','2')), '1º Semestre', '2º Semestre')
    df_final_trim['Período'] = df_final_trim['Trimestre'] + ' (' + df_final_trim['Semestre'] + ')'
    resultados.append(df_final_trim)

    # --- 2. NÍVEL SEMESTRAL ---
    semestres = ['1º Semestre', '2º Semestre']
    df_rascunho_sem = pd.DataFrame(index=pd.MultiIndex.from_product([anos, semestres], names=['Ano', 'Semestre'])).reset_index()
    
    df_real_sem = df_temp.groupby(['Ano', 'Semestre']).agg(agg_dict).reset_index()
    df_real_sem.columns = ['Ano', 'Semestre', 'Qtd Acordos', 'Nomes dos Projetos']
    
    df_final_sem = pd.merge(df_rascunho_sem, df_real_sem, on=['Ano', 'Semestre'], how='left')

    df_final_sem['Período'] = df_final_sem['Semestre']
    df_final_sem['Trimestre'] = '-'
    resultados.append(df_final_sem)

    # --- 3. NÍVEL ANUAL ---
    df_ano = df_temp.groupby(['Ano']).agg(agg_dict).reset_index()
    df_ano.columns = ['Ano', 'Qtd Acordos', 'Nomes dos Projetos']
    df_ano['Período'] = 'Total Ano'
    df_ano['Semestre'] = '-'
    df_ano['Trimestre'] = '-'
    resultados.append(df_ano)

    # Concatena e ordena
    df_final = pd.concat(resultados, ignore_index=True)
    
    # Preenche vazios
    df_final['Qtd Acordos'] = df_final['Qtd Acordos'].fillna(0).astype(int)
    df_final['Nomes dos Projetos'] = df_final['Nomes dos Projetos'].fillna('-')

    # Transforma 'Período' em uma Categoria com ordem definida
    df_final['Período'] = pd.Categorical(
        df_final['Período'], 
        categories=ordem_periodos, 
        ordered=True
    )

    # O Pandas ordena automaticamente baseado na lista 'ordem_periodos'
    df_final = df_final.sort_values(by=['Ano', 'Período'], ascending=[False, True])

    colunas_finais = ['Ano', 'Período', 'Semestre', 'Trimestre', 'Qtd Acordos', 'Nomes dos Projetos']
    
    return df_final[colunas_finais]

# -------- TRIMESTRE E SEMESTRE (FIM) ----------
