import pandas as pd

def projetos_por_segmento(df: pd.DataFrame) -> pd.DataFrame:
    # Exemplo de função utilitária para análise de projetos por segmento
    if 'segmento' not in df.columns:
        raise ValueError("Coluna 'segmento' não encontrada no DataFrame!")
    return df.groupby('segmento').size().reset_index(name='quantidade')

# Adicione aqui outras funções auxiliares específicas para a análise 02
