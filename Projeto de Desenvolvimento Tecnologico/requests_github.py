import re
from datetime import date, datetime
import requests

GITHUB_DATA_URL = "https://api.github.com/repos/propegi-upe/projects-automations/contents/automation/data/backups/technological-development"
BACKUP_PATTERN = r"backup-(\d{4}-\d{2}-\d{2})\.json$"

def extract_date_from_filename(nome_arquivo: str) -> date | None:
    m = re.match(BACKUP_PATTERN, nome_arquivo)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except Exception:
            return None
    return None

def list_available_backups() -> list:
    try:
        response = requests.get(GITHUB_DATA_URL)
        response.raise_for_status()
        files = response.json()
        backups = []
        for file in files:
            filename = file.get("name", "")
            if filename.endswith(".json"):
                data = extract_date_from_filename(filename)
                url = file.get("download_url")
                if data and url:
                    backups.append({
                        "nome_arquivo": filename,
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

def load_backup_json(nome_arquivo: str) -> list:
    try:
        backups = list_available_backups()
        backup = next((b for b in backups if b["nome_arquivo"] == nome_arquivo), None)
        if not backup:
            raise RuntimeError(f"Backup '{nome_arquivo}' não encontrado na lista de backups disponíveis!")
        url = backup["download_url"]
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao baixar o backup JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar o backup JSON: {e}")

def load_all_backups() -> dict:
    try:
        backups = list_available_backups()
        all_data = {}
        for b in backups:
            filename = b["nome_arquivo"]
            url = b["download_url"]
            try:
                response = requests.get(url)
                response.raise_for_status()
                all_data[filename] = response.json()
            except Exception as e:
                all_data[filename] = f"Erro ao baixar: {e}"
        return all_data
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar todos os backups: {e}")

def get_latest_backup_metadata() -> dict:
    try:
        response = requests.get(GITHUB_DATA_URL)
        response.raise_for_status()
        files = response.json()
        backups = []
        for file in files:
            filename = file.get("name", "")
            if filename.endswith(".json"):
                data = extract_date_from_filename(filename)
                if data:
                    backups.append((data, file))
        if not backups:
            raise RuntimeError("Nenhum arquivo de backup JSON encontrado no GitHub!")
        backups.sort(reverse=True)
        return backups[0][1]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao buscar backups no GitHub: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao processar arquivos de backup: {e}")

def load_latest_backup_json() -> dict | list:
    try:
        metadata = get_latest_backup_metadata()
        url = metadata.get("download_url")
        if not url:
            raise RuntimeError("Campo 'download_url' não encontrado no metadata do backup!")
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro de rede ao baixar o backup JSON: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar o backup JSON: {e}")
