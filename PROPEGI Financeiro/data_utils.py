from pathlib import Path
import json
import pandas as pd

# Este módulo é um "DataTools": ele centraliza a etapa de TRATAMENTO e PADRONIZAÇÃO dos dados.
# A importância disso é garantir que o restante do projeto (gráficos, métricas e dashboards)
# trabalhe com tipos consistentes (datas como números, valores monetários como float, etc.).

# Mapeamento de meses (texto) -> número do mês.
# Importante para:
# - ordenar corretamente no tempo (Jan, Fev, Mar...)
# - criar séries temporais e gráficos mensais sem “bagunça” alfabética
MONTHS = {
    "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
    "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
    "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
}


def convert_br_value_to_float(value_str):
    """
    Converte valores monetários no formato brasileiro para float.

    Por que isso é importante?
    - Dados podem vir como texto (ex.: "1.234,56") e, para calcular soma/média/indicadores,
      precisamos de um número (float).
    - Também tratamos casos vazios/invalidos para evitar quebrar o pipeline de análise.
    """
    # Se vier vazio/nulo, assumimos 0.0 para manter consistência e evitar erros em cálculos.
    if value_str is None or value_str == "":
        return 0.0

    # Se o valor já veio numérico (int/float), apenas padronizamos para float.
    if isinstance(value_str, (int, float)):
        return float(value_str)

    # Formato BR usa: "." como separador de milhar e "," como separador decimal.
    # Aqui removemos os pontos e trocamos vírgula por ponto para o Python conseguir converter.
    clean_value = str(value_str).replace(".", "").replace(",", ".")

    # Se a conversão falhar (ex.: texto inesperado), retornamos 0.0 para não interromper o fluxo.
    try:
        return float(clean_value)
    except ValueError:
        return 0.0



def load_data(input_folder="input"):
    """
    Carrega todos os arquivos JSON de uma pasta e retorna um DataFrame unificado.

    Por que isso é importante?
    - Em projetos reais, dados costumam vir em vários arquivos (por mês, por extração, por setor).
    - Unificar tudo em um único DataFrame facilita análises, filtros e geração de relatórios.
    - Também padronizamos tipos/colunas para garantir que gráficos e KPIs não falhem depois.
    """
    path = Path(input_folder)

    # Validamos a existência da pasta para dar um erro claro e rápido (evita "erro silencioso").
    if not path.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {path}")

    # Buscamos todos os JSONs da pasta.
    json_files = list(path.glob("*.json"))

    # Se não houver arquivos, paramos com uma mensagem clara (evita gerar DataFrame vazio sem perceber).
    if not json_files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em: {path}")

    # Guardamos DataFrames intermediários para depois juntar tudo.
    dataframes = []

    # Lemos cada JSON e transformamos em DataFrame.
    # Importante: isso padroniza o formato para operar com pandas (filtros, joins, agregações, etc.).
    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        df_temp = pd.DataFrame(data)
        dataframes.append(df_temp)

    # Unifica todos os arquivos em um único DataFrame.
    # ignore_index=True: recria o índice do zero para evitar índices repetidos entre arquivos.
    df = pd.concat(dataframes, ignore_index=True)

    # ---------- Tratamentos essenciais para análise ----------
    # 1) Convertendo mês textual para número:
    #    isso permite ordenação temporal e construção de séries mensais corretamente.
    df["numeroMes"] = df["mes"].map(MONTHS)

    # 2) Convertendo valores monetários para float:
    #    isso permite calcular totais, médias, percentuais e qualquer KPI financeiro.
    df["valorFloat"] = df["valorDaFolha"].apply(convert_br_value_to_float)

    # 3) Garantindo que o ano é inteiro:
    #    isso evita problemas em filtros (ex.: comparar "2024" string com 2024 int).
    df["ano"] = df["ano"].astype(int)

    return df


def filter_by_year(df, years):
    """
    Filtra o DataFrame por anos selecionados.

    Importância:
    - Permite que dashboards e análises comparem períodos específicos (ex.: 2023 vs 2024).
    - Se 'anos' vier vazio, retornamos o dataset completo (comportamento útil em telas com filtros).
    """
    if not years:
        return df
    return df[df["ano"].isin(years)]


def filter_by_project(df, projects):
    """
    Filtra o DataFrame por nomes de projetos.

    Importância:
    - Permite recortar a análise por projeto (ex.: um KPI por projeto, ranking, evolução mensal).
    - Se 'projetos' vier vazio, retornamos o dataset completo para não “sumir” dados no dashboard.
    """
    if not projects:
        return df
    return df[df["nomeProjeto"].isin(projects)]
