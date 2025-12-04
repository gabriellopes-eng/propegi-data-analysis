import requests
import re
from datetime import datetime, date

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
