from data_utils import carregar_ultimo_backup_json

# Teste simples para validar recebimento dos dados da API do GitHub
if __name__ == "__main__":
    dados = carregar_ultimo_backup_json()
    print(f"Tipo dos dados: {type(dados)}")
    print(f"Quantidade de projetos: {len(dados)}")
    if len(dados) > 0:
        print("Primeiro projeto:")
        print(dados[0])
    else:
        print("Nenhum projeto encontrado no backup JSON.")
