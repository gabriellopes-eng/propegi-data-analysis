from data_utils import listar_backups_disponiveis, carregar_backup_json, carregar_todos_os_backups

if __name__ == "__main__":
    print("Testando listar_backups_disponiveis...")
    backups = listar_backups_disponiveis()
    print("Backups disponíveis:")
    for b in backups:
        print(f"Arquivo: {b['nome_arquivo']}, Data: {b['data_backup']}, URL: {b['download_url']}")

    if backups:
        nome = backups[0]["nome_arquivo"]
        print(f"\nTestando carregar_backup_json para {nome}...")
        projetos = carregar_backup_json(nome)
        print(f"{nome}: {len(projetos)} projetos")
        print("Primeiro projeto:", projetos[0] if projetos else "Nenhum projeto")

    print("\nTestando carregar_todos_os_backups...")
    todos = carregar_todos_os_backups()
    for nome, lista in todos.items():
        if isinstance(lista, list):
            print(f"{nome}: {len(lista)} projetos")
        else:
            print(f"{nome}: {lista}")
