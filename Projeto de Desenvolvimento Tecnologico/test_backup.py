import re
import requests
import pandas as pd
from data_utils import list_available_backups, load_backup_json

# Utilitários para testes e validação 
def carregar_json_url(url: str):
    """Carrega um JSON remoto e retorna um DataFrame pandas."""
    response = requests.get(url)
    response.raise_for_status()
    return pd.DataFrame(response.json())

def get_url_padrao():
    """Retorna a URL do último backup disponível no GitHub."""
    from data_utils import get_latest_backup_metadata
    meta = get_latest_backup_metadata()
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
        backup_files = [
            f["name"] for f in files if re.match(r"backup-\\d{4}-\\d{2}-\\d{2}\\.json$", f["name"])
        ]
        if not backup_files:
            raise Exception("Nenhum backup encontrado.")
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

if __name__ == "__main__":
    print("Testando backup mais recente:")
    url = get_url_padrao()
    try:
        df = carregar_json_url(url)
        print(f"Tipo dos dados: {type(df)}")
        print(f"Quantidade de registros: {len(df)}")
        if len(df) > 0:
            print("Primeiro registro do backup mais recente:")
            print(df.iloc[0])
            print("Último registro do backup mais recente:")
            print(df.iloc[-1])
        else:
            print("Nenhum registro encontrado no JSON.")
    except Exception as e:
        print(f"Erro ao carregar dados da API: {e}")

    print("\nTestando seleção de backup específico:")
    try:
        backups = list_available_backups()
        print("Backups disponíveis:")
        for idx, b in enumerate(backups):
            print(f"[{idx}] {b['nome_arquivo']} (data: {b['data_backup']})")
        choice = input("Selecione o número do backup desejado: ")
        idx = int(choice)
        filename = backups[idx]["nome_arquivo"]
        data = load_backup_json(filename)
        print(f"Tipo dos dados: {type(data)}")
        print(f"Quantidade de registros: {len(data)}")
        if len(data) > 0:
            print("")
            print("Primeiro registro do backup selecionado:")
            print(df.iloc[0])
            print("")
            print("Último registro do backup selecionado:")
            print(df.iloc[-1])
        else:
            print("Nenhum registro encontrado no JSON.")
    except Exception as e:
        print(f"Erro ao carregar dados do backup: {e}")

#cd '.\Projeto de Desenvolvimento Tecnologico\'
#python test_backup.py - Pelo Terminal. Ou so rodar no ambiente de desenvolvimento.