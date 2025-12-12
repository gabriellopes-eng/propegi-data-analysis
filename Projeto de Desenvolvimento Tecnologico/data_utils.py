from __future__ import annotations
import re
from datetime import date, datetime
from pathlib import Path
import pandas as pd
import requests
import numpy as np

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

# Utilitários para testes
def carregar_json_url(url: str):
    """Carrega um JSON remoto e retorna um DataFrame pandas."""
    import pandas as pd
    resposta = requests.get(url)
    resposta.raise_for_status()
    return pd.DataFrame(resposta.json())

def get_url_padrao():
    """Retorna a URL do último backup disponível no GitHub."""
    meta = obter_metadata_ultimo_backup()
    return meta.get("download_url")

def get_latest_backup_url():
    """
    Busca o backup mais recente disponível no repositório do GitHub.
    Retorna a URL do arquivo JSON mais recente.
    """
    api_url = (
        "https://api.github.com/repos/propegi-upe/projects-automations/contents/automation/data/backups/technological-development"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()
        # Regex para datas no formato backup-YYYY-MM-DD.json
        backup_files = [
            f["name"] for f in files if re.match(r"backup-\\d{4}-\\d{2}-\\d{2}\\.json$", f["name"])
        ]
        if not backup_files:
            raise Exception("Nenhum backup encontrado.")
        # Ordena por data decrescente
        backup_files.sort(reverse=True)
        latest = backup_files[0]
        return f"https://raw.githubusercontent.com/propegi-upe/projects-automations/main/automation/data/backups/technological-development/{latest}"
    except Exception as e:
        print(f"Erro ao buscar backups: {e}")
        return None

def carregar_json_backup_mais_recente():
    """
    Baixa e carrega o backup mais recente disponível.
    """
    url = get_latest_backup_url()
    if not url:
        print("Backup mais recente não encontrado.")
        return pd.DataFrame()
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Erro ao baixar backup mais recente: {e}")
        return pd.DataFrame()


# Raiz do projeto (pasta onde está este arquivo)
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"

# Nome padrão do JSON (ajuste se necessário)
DEFAULT_JSON_NAME = "Projetos de Desenvolvimento Tecnologico.json" # necessário apenas para os dados estáticos

BRL_COLS = [
    "valorPactuado",
    "valorAgencia",
    "valorUnidade",
    "valorIAUPE",
]

def input_path(name: str | Path = DEFAULT_JSON_NAME) -> Path: # necessário apenas para os dados estáticos
    """Retorna o caminho absoluto dentro de input/."""
    p = INPUT_DIR / name
    if not p.exists():
        raise FileNotFoundError(f"Arquivo não encontrado em: {p}")
    return p

def carregar_json(path: str | Path | None = None) -> pd.DataFrame: # necessário apenas para os dados estáticos
    """
    Lê o JSON (lista de objetos) e retorna um DataFrame.
    Se path for None, usa input/DEFAULT_JSON_NAME.
    """
    if path is None:
        path = input_path(DEFAULT_JSON_NAME)
    return pd.read_json(path)

def carregar_json_backup():
    url = "https://raw.githubusercontent.com/propegi-upe/projects-automations/refs/heads/main/automation/data/backups/technological-development/backup-2025-12-02.json"

    try:
        response = requests.get(url)

        # Verifica erro HTTP
        response.raise_for_status()

        # 1. Converte para JSON (Define a variável 'data')
        data = response.json()

        df = pd.DataFrame(data) 
        
        return df

        # Converte para JSON
        data = response.json()
        print(data)

    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP ao obter o JSON: {e}")
        return pd.DataFrame() # <--- RETORNA DATAFRAME VAZIO EM CASO DE ERRO HTTP
    except Exception as e:
        print(f"Erro ao obter o JSON: {e}")
        return pd.DataFrame() # <--- RETORNA DATAFRAME VAZIO EM CASO DE ERRO HTTP

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

    # -------------- MODIFICAÇAO 19/11 (INÍCIO) --------------
    # Colunas de data a serem convertidas
    date_cols = ["dataPublicacao", "inicioData", "terminoData"]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    # -------------- MODIFICAÇAO 19/11 (FIM) --------------

    #df["dataPublicacao"] = pd.to_datetime(df["dataPublicacao"], errors="coerce") # verificar se não é uma redundância
    df["Ano"] = df["dataPublicacao"].dt.year
    df["Mes"] = df["dataPublicacao"].dt.month
    df["MesNome"] = df["dataPublicacao"].dt.strftime("%m/%b")
    return df

# -------------- MODIFICAÇAO 26/11 (INÍCIO) --------------

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

# -------------- MODIFICAÇAO 26/11 (FIM) --------------

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

# -------- TRIMESTRE E SEMESTRE (INÍCIO) ----------

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
    df_temp['Mes'] = df_temp['inicioData'].dt.month
    df_temp['Trimestre'] = df_temp['inicioData'].dt.quarter.astype(int).astype(str) + 'º Trimestre'
    df_temp['Semestre'] = np.where(df_temp['Mes'] <= 6, '1º Semestre', '2º Semestre')
    
    # Função auxiliar para listar nomes com ponto e vírgula
    def listar_nomes(serie: pd.Series) -> str:
        return '; '.join(serie.sort_values().astype(str).tolist())

    # Dicionário de Agregação
    agg_dict = {
        'nomeProjeto': [
            ('Qtd Acordos', 'count'), 
            ('Nomes dos Projetos', listar_nomes) 
        ]
    }
    
    resultados = []

    # 1. Agregação por Trimestre
    # Agrupa por 3 níveis, mas depois simplifica para visualização
    df_trim = df_temp.groupby(['Ano', 'Semestre', 'Trimestre']).agg(agg_dict).reset_index()
    df_trim.columns = ['Ano', 'Semestre', 'Período', 'Qtd Acordos', 'Nomes dos Projetos']
    # Adiciona o semestre ao nome do período para clareza
    df_trim['Período'] = df_trim['Período'] + ' (' + df_trim['Semestre'] + ')'
    resultados.append(df_trim[['Ano', 'Período', 'Qtd Acordos', 'Nomes dos Projetos']])

    # 2. Agregação por Semestre
    df_sem = df_temp.groupby(['Ano', 'Semestre']).agg(agg_dict).reset_index()
    df_sem.columns = ['Ano', 'Período', 'Qtd Acordos', 'Nomes dos Projetos']
    resultados.append(df_sem)

    # 3. Agregação por Ano
    df_ano = df_temp.groupby(['Ano']).agg(agg_dict).reset_index()
    df_ano.columns = ['Ano', 'Qtd Acordos', 'Nomes dos Projetos']
    df_ano['Período'] = 'Total Ano'
    resultados.append(df_ano)

    # Concatena e ordena
    df_final = pd.concat(resultados, ignore_index=True)
    return df_final.sort_values(by=['Ano', 'Qtd Acordos'], ascending=[False, False])

# -------- TRIMESTRE E SEMESTRE (FIM) ----------
