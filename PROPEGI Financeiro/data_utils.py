from pathlib import Path
import json
import pandas as pd

# mapeamento de Meses para números
MESES = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}

# converte valores em formato brasileiro para float
def converter_valor_br_para_float(valor_str):
    if valor_str is None or valor_str == "":
        return 0.0
    
    if isinstance(valor_str, (int, float)):
        return float(valor_str)
    
    # remove pontos e troca vírgula por ponto
    valor_limpo = str(valor_str).replace(".", "").replace(",", ".")
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0


#carrega todos os JSONs da pasta e retorna um DataFrame unificado
def carregar_dados(pasta_input="input"):
    pasta = Path(pasta_input)
    
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {pasta}")
    
    # busca todos os arquivos .json na pasta
    arquivos_json = list(pasta.glob("*.json"))
    
    if not arquivos_json:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em: {pasta}")
    
    # Lista para armazenar DataFrames de cada arquivo
    dataframes = []
    
    # Lê cada JSON e adiciona na lista
    for arquivo in arquivos_json:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        df_temp = pd.DataFrame(dados)
        dataframes.append(df_temp)
    
    # Junta todos os DataFrames em um só
    df = pd.concat(dataframes, ignore_index=True)
    
    # Conversões importantes para garantir os tipos corretos
    df["numeroMes"] = df["mes"].map(MESES)
    df["valorFloat"] = df["valorDaFolha"].apply(converter_valor_br_para_float)
    df["ano"] = df["ano"].astype(int)
    
    return df

# Serve para filtrar o DataFrame por ano 
def filtrar_por_ano(df, anos):
    """Filtra o DataFrame por lista de anos."""
    if not anos:
        return df
    return df[df["ano"].isin(anos)]

# Serve para filtrar o DataFrame por projeto
def filtrar_por_projeto(df, projetos):
    """Filtra o DataFrame por lista de nomes de projetos."""
    if not projetos:
        return df
    return df[df["nomeProjeto"].isin(projetos)]