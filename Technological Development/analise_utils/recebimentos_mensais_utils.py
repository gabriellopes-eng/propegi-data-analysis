def brl(v: float) -> str:
    """Formata float para BRL simples (R$ 1.234,56)."""
    s = f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"
import pandas as pd

def normalizar_valores(df: pd.DataFrame) -> pd.DataFrame:
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
    BRL_COLS = [
        "valorPactuado",
        "valorAgencia",
        "valorUnidade",
        "valorIAUPE",
    ]
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

def acordos_recentes(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    df_ordenado = df_copy.sort_values(by='inicioData', ascending=False)
    return df_ordenado.head(5)

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
