from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from pandas.api.types import is_numeric_dtype
from typing import Iterable, Optional, Union
from itertools import chain

# Meus Meses na ordem certa (1..12)
MESES = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}

def _to_float(valor):
    """
    Converte '32617,27' -> 32617.27 e mantém números já numéricos.
    Também lida com None/vazio retornando 0.0 para evitar quebras.
    """
    if valor is None: #Tratei para caso venha Valor da folha como None
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    txt = str(valor).strip().replace(".", "")  # Se caso venha separador de milhar, o que é raro
    txt = txt.replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return 0.0

def carregar_financas_json(caminho_arquivo: str | Path) -> pd.DataFrame:
    """
    Lê o JSON de finanças e devolve um DataFrame com:
    - 'Projetos', 'Ano', 'Mês', 'Número do mês', 'Valor da folha' (float)
    - coluna extra 'AnoMes' no formato '2021-Jan' (ordenável por 'Número do mês')
    """
    caminho = Path(caminho_arquivo)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho.resolve()}")

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    df = pd.DataFrame(dados)
    return _normalize_financas_df(df)

def filtrar(df: pd.DataFrame, anos: list[int] | None, projetos: list[str] | None) -> pd.DataFrame:
    """Aplica filtros simples por ano e projetos (se fornecidos)."""
    out = df.copy()
    if anos:
        out = out[out["Ano"].isin(anos)]
    if projetos:
        out = out[out["Projetos"].isin(projetos)]
    return out

# Importante: função usada para as análises de Taxa e Plano de Trabalho
def somatorio_por_taxa_plano(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa e soma 'Valor da folha' por projeto, taxa e plano de trabalho.
    Garante que as colunas 'Taxa' e 'Plano de Trabalho' existam.
    Retorna DataFrame pronto para exportar como JSON.
    """
    df = df.copy()
    if "Taxa" not in df.columns: #Serve para evitar erro se a coluna taxa não existir
        df["Taxa"] = "N/A"
    if "Plano de Trabalho" not in df.columns: #Serve para evitar erro se a coluna plano de trabalho não existir
        df["Plano de Trabalho"] = "N/A"

    agrupado = df.groupby([
        "Projeto_ID", "Projetos", "Projeto de Origem", "Ano", "Mês", "Número do mês", "Taxa", "Plano de Trabalho"
    ], dropna=False, as_index=False)["Valor da folha"].sum()
    return agrupado


def validar_financas_df(
    df: pd.DataFrame,
    expected_years: Optional[Iterable[int]] = None,
) -> list[str]:
    """
    Validações simples do dataset de finanças.
    - Se expected_years for fornecido, valida se os anos do DF estão dentro do conjunto esperado.
    - Sempre valida: tipo/na de 'Valor da folha' e faixa válida para 'Número do mês'.
    Retorna lista de mensagens de alerta (vazia se tudo ok).
    """
    issues: list[str] = []

    # 1) Anos dentro do esperado (opcional)
    if expected_years is not None:
        try:
            anos = sorted(int(a) for a in df["Ano"].dropna().unique())
            expected_set = set(int(a) for a in expected_years)
            fora_intervalo = [a for a in anos if a not in expected_set]
            if fora_intervalo:
                issues.append(
                    f"Ano(s) fora do conjunto esperado {sorted(expected_set)}: {fora_intervalo}"
                )
        except Exception:
            issues.append("Coluna 'Ano' não está no formato esperado (inteiro).")

    # 2) Valor da folha numérico e não nulo
    if "Valor da folha" not in df.columns:
        issues.append("Coluna 'Valor da folha' ausente no dataset.")
    else:
        if not is_numeric_dtype(df["Valor da folha"]):
            issues.append("Coluna 'Valor da folha' não é numérica após a conversão.")
        nulos = int(df["Valor da folha"].isna().sum())
        if nulos > 0:
            issues.append(f"Existem {nulos} registros com 'Valor da folha' nulo.")

    # 3) Número do mês válido
    if "Número do mês" not in df.columns:
        issues.append("Coluna 'Número do mês' ausente no dataset.")
    else:
        try:
            inval = df[(df["Número do mês"] < 1) | (df["Número do mês"] > 12)]
            if not inval.empty:
                qtd = len(inval)
                issues.append(f"{qtd} registro(s) com 'Número do mês' fora de 1..12.")
        except Exception:
            issues.append("Coluna 'Número do mês' não está no formato numérico esperado.")

    return issues


# -------------------- Funções utilitárias avançadas (futuro-proof) --------------------

def _normalize_financas_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza o DataFrame de finanças:
    - Garante colunas essenciais
    - Converte "Valor da folha" para float (pt-BR -> float)
    - Garante numéricos em "Ano" e "Número do mês"
    - Cria colunas temporais: MesAbrev, AnoMes, ord_col
    """
    df = df.copy()

    # Colunas essenciais
    colunas_essenciais = ["Projetos", "Ano", "Mês", "Número do mês", "Valor da folha"]
    faltando = [c for c in colunas_essenciais if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes no JSON: {faltando}")

    # Coerção de tipos
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce").astype("Int64")
    df["Número do mês"] = pd.to_numeric(df["Número do mês"], errors="coerce").astype("Int64")

    # Valor da folha para float
    df["Valor da folha"] = df["Valor da folha"].apply(_to_float)

    # Colunas temporais
    df["MesAbrev"] = df["Número do mês"].map(MESES).fillna(df["Mês"])
    df["AnoMes"] = df["Ano"].astype(str) + "-" + df["MesAbrev"].astype(str)
    # ord_col: se Ano/Numero do mes estiverem nulos, resultará em <NA>; lidaremos convertendo para int quando possível
    df["ord_col"] = df["Ano"].astype("Int64") * 100 + df["Número do mês"].astype("Int64")

    return df


def carregar_financas(
    caminhos: Union[str, Path, Iterable[Union[str, Path]]],
    adicionar_coluna_origem: bool = True,
) -> pd.DataFrame:
    """
    Carrega um ou vários arquivos JSON de finanças e concatena em um único DataFrame normalizado.

    caminhos pode ser:
    - str/Path para um arquivo
    - str/Path para uma pasta (carrega *.json)
    - str com wildcard (glob), ex: "input/Financas_*.json"
    - Iterable de str/Path (lista de arquivos)

    Se adicionar_coluna_origem=True, adiciona coluna "Arquivo" com o nome/base do arquivo.
    """
    paths: list[Path] = []

    def _coletar(p: Union[str, Path]):
        pth = Path(p)
        if any(ch in str(pth) for ch in ["*", "?", "["]):
            # padrão glob
            paths.extend(Path().glob(str(pth)))
        elif pth.is_dir():
            paths.extend(sorted(pth.glob("*.json")))
        else:
            paths.append(pth)

    if isinstance(caminhos, (str, Path)):
        _coletar(caminhos)
    else:
        for c in caminhos:
            _coletar(c)

    if not paths:
        raise FileNotFoundError("Nenhum arquivo JSON encontrado para carregar.")

    dflist: list[pd.DataFrame] = []
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {p}")
        with open(p, "r", encoding="utf-8") as f:
            dados = json.load(f)
        df_raw = pd.DataFrame(dados)
        df_norm = _normalize_financas_df(df_raw)
        if adicionar_coluna_origem:
            df_norm["Arquivo"] = p.name
        dflist.append(df_norm)

    df_total = pd.concat(dflist, ignore_index=True)
    return df_total


def detectar_duplicatas(
    df: pd.DataFrame,
    chaves: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Retorna DataFrame com linhas duplicadas considerando as chaves fornecidas.
    Padrão de chaves: ("Projetos", "Ano", "Número do mês")
    """
    if chaves is None:
        chaves = ("Projetos", "Ano", "Número do mês")
    mask = df.duplicated(subset=list(chaves), keep=False)
    return df.loc[mask].sort_values(list(chaves))