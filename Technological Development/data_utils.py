# --- Função para retornar os 5 projetos mais recentes ---
def acordos_recentes(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    df_ordenado = df_copy.sort_values(by='inicioData', ascending=False)
    return df_ordenado.head(5)

# --- IMPORTS NO TOPO ---
import pandas as pd
import requests
import re
from datetime import datetime, date

# --- Funções para imputação de ano do projeto ---
def _extrair_ano_do_acordo(serie_acordo: pd.Series) -> pd.Series:
    serie = serie_acordo.astype(str).str.split('-').str[-1]
    return pd.to_numeric(serie, errors='coerce')

def imputar_data_projeto(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['AnoAcordo'] = _extrair_ano_do_acordo(df['acordoConvenioNumero'])
    df['Ano'] = df['Ano'].fillna(df['inicioData'].dt.year)
    df['Ano'] = df['Ano'].fillna(df['AnoAcordo'])
    df = df.drop(columns=['AnoAcordo'], errors='ignore')
    df['Ano'] = df['Ano'].fillna(9999).astype(int).astype(str).replace('9999', 'Não Definido')
    return df

# --- Funções auxiliares para análise dos dados dos backups ---
BRL_COLS = [
    "valorPactuado",
    "valorAgencia",
    "valorUnidade",
    "valorIAUPE",
]

def _br_to_float(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    serie = serie.fillna("0").astype(str).str.strip()
    serie = serie.str.replace(r'[^\d\.\,]', '', regex=True)
    serie = serie.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(serie, errors="coerce").fillna(0.0)

def normalizar_valores(df: pd.DataFrame) -> pd.DataFrame:
    for c in BRL_COLS:
        if c in df.columns:
            df[c] = _br_to_float(df[c])
    return df

def preparar_datas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in ["dataPublicacao", "inicioData", "terminoData"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "dataPublicacao" in df.columns:
        df["Ano"] = df["dataPublicacao"].dt.year
        df["Mes"] = df["dataPublicacao"].dt.month
        df["MesNome"] = df["dataPublicacao"].dt.strftime("%m/%b")
    return df

def agrupar_mensal(df: pd.DataFrame, ano: int) -> pd.DataFrame:
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
    return {
        "agencia": float(df_mes["valorAgencia"].sum()) if "valorAgencia" in df_mes else 0.0,
        "unidade": float(df_mes["valorUnidade"].sum()) if "valorUnidade" in df_mes else 0.0,
        "ia_upe": float(df_mes["valorIAUPE"].sum()) if "valorIAUPE" in df_mes else 0.0,
    }

# URL da API de conteúdos do GitHub
URL_CONTEUDOS_GITHUB = "https://api.github.com/repos/propegi-upe/projects-automations/contents/automation/data/backups/technological-development"
PADRAO_BACKUP = r"backup-(\d{4}-\d{2}-\d{2})\.json$"

def extrair_data_do_nome(nome_arquivo: str) -> date | None:
    """
    Extrai a data do nome do arquivo no formato backup-YYYY-MM-DD.json
    """
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
import requests
import re

# URL da API de conteúdos do GitHub
URL_CONTEUDOS_GITHUB = "https://api.github.com/repos/propegi-upe/projects-automations/contents/automation/data/backups/technological-development"
PADRAO_BACKUP = r"backup-(\d{4}-\d{2}-\d{2})\.json$"

def extrair_data_do_nome(nome_arquivo: str) -> str | None:
    """
    Extrai a data do nome do arquivo no formato backup-YYYY-MM-DD.json
    """
    m = re.match(PADRAO_BACKUP, nome_arquivo)
    if m:
        return m.group(1)
    return None

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
