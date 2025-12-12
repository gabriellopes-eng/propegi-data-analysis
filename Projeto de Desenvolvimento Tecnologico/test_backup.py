from data_utils import listar_backups_disponiveis, carregar_backup_json, carregar_json_url, get_url_padrao

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
        backups = listar_backups_disponiveis()
        print("Backups disponíveis:")
        for idx, b in enumerate(backups):
            print(f"[{idx}] {b['nome_arquivo']} (data: {b['data_backup']})")
        escolha = input("Selecione o número do backup desejado: ")
        idx = int(escolha)
        nome_arquivo = backups[idx]["nome_arquivo"]
        dados = carregar_backup_json(nome_arquivo)
        print(f"Tipo dos dados: {type(dados)}")
        print(f"Quantidade de registros: {len(dados)}")
        if len(dados) > 0:
            print("Primeiro registro do backup selecionado:")
            print(dados[0])
            print("Último registro do backup selecionado:")
            print(dados[-1])
        else:
            print("Nenhum registro encontrado no JSON.")
    except Exception as e:
        print(f"Erro ao carregar dados do backup: {e}")

#cd '.\Projeto de Desenvolvimento Tecnologico\'
#python test_backup.py - Pelo Terminal. Ou so rodar no ambiente de desenvolvimento.