import pandas as pd

def recebimentos_por_setor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os valores recebidos por Agência, Unidade e IA-UPE por ano e setor (segmento).
    Retorna um DataFrame com as somas anuais por segmento.
    """
    if 'segmento' not in df.columns:
        raise ValueError("Coluna 'segmento' não encontrada no DataFrame!")
    return (
        df.groupby(["Ano", "segmento"])[["valorAgencia", "valorUnidade", "valorIAUPE"]]
          .sum()
          .reset_index()
          .sort_values(["Ano", "segmento"])
    )
