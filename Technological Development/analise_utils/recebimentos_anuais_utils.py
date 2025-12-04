import pandas as pd

def agrupar_recebimentos_anuais(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa os valores recebidos por Agência, Unidade e IA-UPE por ano.
    Retorna um DataFrame com as somas anuais.
    """
    return (
        df.groupby("Ano")[["valorAgencia", "valorUnidade", "valorIAUPE"]]
          .sum()
          .reset_index()
          .sort_values("Ano")
    )

def totais_acumulados(df_group: pd.DataFrame) -> dict:
    """
    Calcula os totais acumulados para cada órgão.
    """
    return {
        "agencia": float(df_group["valorAgencia"].sum()),
        "unidade": float(df_group["valorUnidade"].sum()),
        "iaupe": float(df_group["valorIAUPE"].sum()),
    }

def ano_pico(df_group: pd.DataFrame) -> tuple:
    """
    Retorna o ano e valor do ano com maior soma total entre os órgãos.
    """
    df_group = df_group.copy()
    df_group["TotalAno"] = (
        df_group["valorAgencia"] + df_group["valorUnidade"] + df_group["valorIAUPE"]
    )
    idx_pico = df_group["TotalAno"].idxmax()
    ano = int(df_group.loc[idx_pico, "Ano"])
    valor = float(df_group.loc[idx_pico, "TotalAno"])
    return ano, valor
