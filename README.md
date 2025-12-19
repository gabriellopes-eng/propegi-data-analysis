---

## Como testar o carregamento de backups (test_backup.py)

O projeto inclui um script de teste para validar o carregamento dos backups de dados diretamente do GitHub. Ele permite:
- Verificar se o backup mais recente está acessível e válido
- Listar todos os backups disponíveis
- Selecionar e inspecionar qualquer backup manualmente

### Como rodar o teste (Windows PowerShell ou terminal Unix)

1. Ative o ambiente virtual (caso ainda não esteja ativado):

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  ou, no bash/zsh:
  ```bash
  source .venv/bin/activate
  ```

2. Execute o script de teste:

  ```powershell
  python Projeto de Desenvolvimento Tecnologico/test_backup.py
  ```
  ou, no bash/zsh:
  ```bash
  python 'Projeto de Desenvolvimento Tecnologico/test_backup.py'
  ```

O script irá:
- Mostrar informações do backup mais recente
- Listar todos os backups disponíveis
- Permitir que você selecione um backup para inspecionar os dados

Se houver algum erro de conexão ou leitura, o script exibirá mensagens detalhadas para facilitar o diagnóstico.
# ◈ Data Analysis UPE

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.20.0-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<!-- teste -->


Dashboards interativos em **Streamlit** para dois domínios principais, com dados carregados dinamicamente de backups hospedados no GitHub:


- **PROPEGI Financeiro**
- **Projeto de Desenvolvimento Tecnológico**


Os apps não dependem mais de arquivos locais na pasta `input/` para análise: os dados são buscados automaticamente do backup mais recente disponível no repositório do GitHub, tornando o sistema robusto e sempre atualizado.

---

## Requisitos

- Python 3.10+ (recomendado)
- Git (opcional para clonar)
- Dependências do projeto listadas em `requirements.txt`


Observação: o projeto usa principalmente `streamlit`, `pandas`, `plotly` e `numpy`. Todas as análises são dinâmicas e robustas, com storytelling e validações automáticas em cada página.

---

## 1) Clonar o repositório

```powershell
git clone https://github.com/propegi-upe/propegi-data-analysis.git
cd 'propegi-data-analysis'
```

---

## 2) Criar e ativar ambiente virtual (OBRIGATÓRIO)

⚠️ **IMPORTANTE**: É obrigatório usar um ambiente virtual para evitar conflitos com outros projetos Python.
Vamos criar um ambiente chamado `.venv` na raiz do repositório.

Windows (PowerShell):

```powershell
python -m venv .venv
# Ativar (PowerShell)
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a execução do script de ativação por política de execução, rode (apenas para a sessão atual):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Confirm:$false
```

Linux / macOS (bash / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

fish shell (ex.: quando o professor pediu para usar `fish`):

```fish
python3 -m venv .venv
source .venv/bin/activate.fish
```

---

## 3) Instalar dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

Se precisar de pacotes de desenvolvimento (formatadores, linter, testes), posso adicionar `requirements-dev.txt` — me avise.

---

## 4) Estrutura relevante do projeto

- `Projeto de Desenvolvimento Tecnologico/`


  - `app.py` — app Streamlit principal deste domínio
  - `data_utils.py`, `pages/` — utilitários e páginas auxiliares

- `PROPEGI Financeiro/`

  - `app.py` — app Streamlit principal do domínio financeiro
  - `data_utils.py`, `pages/` — utilitários e páginas auxiliares

---

## 5) Como executar os apps (exemplos)

⚠️ **MUITO IMPORTANTE**:

1. **SEMPRE** ative o ambiente virtual (`.venv`) antes de rodar (veja passo 2)
2. **NUNCA** tente rodar sem ativar o ambiente virtual, pois as dependências não estarão disponíveis
3. **O MESMO** ambiente virtual (`.venv`) serve para rodar os dois projetos! Não precisa criar um novo

💡 **Dica**: Depois que o ambiente virtual estiver ativado, você pode rodar qualquer um dos dois projetos (ou os dois ao mesmo tempo em terminais diferentes)!

PowerShell (Windows) — PROPEGI Financeiro:

```powershell
cd 'c:\Users\Elward\Documents\repositorios\propegi-data-analysis\PROPEGI Financeiro'
streamlit run app.py
```

PowerShell (Windows) — Projeto de Desenvolvimento Tecnologico:

```powershell
cd 'c:\Users\Elward\Documents\repositorios\propegi-data-analysis\Projeto de Desenvolvimento Tecnologico'
streamlit run app.py
```

fish / bash / zsh (Unix-like) — exemplo (ajuste o caminho):

```bash
cd 'PROPEGI Financeiro'
streamlit run app.py
```

Observação: os caminhos acima assumem que você está na máquina local onde o repositório foi clonado. Ajuste os caminhos conforme sua organização de pastas.

---

## 6) Dicas rápidas / resolução de problemas

- Erro "module not found" para `streamlit` ou `pandas`:
  - **Causa mais comum**: ambiente virtual não está ativado
  - **Solução**:
    1. Ative o ambiente virtual (`.venv`) seguindo o passo 2
    2. Execute `pip install -r requirements.txt` novamente
    3. Confirme que está ativado verificando se aparece `(.venv)` no início do prompt
- Erro ao ativar `.venv` no PowerShell:
  - Execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Confirm:$false` na sessão atual e tente ativar novamente.
- Arquivo JSON não encontrado:
  - Os dados são carregados automaticamente do backup mais recente do GitHub. Não é necessário manter arquivos JSON locais na pasta `input/` para as análises funcionarem.
- Selectbox com lista vazia (Streamlit):
  - Se uma página usa `st.selectbox(..., index=0)` e não existem opções, Streamlit pode lançar erro. Todas as páginas já possuem validação para evitar esse problema.

---


## 7) Funcionalidades avançadas e testes

- Testes automatizados para validação e recuperação de backups dos dados estão disponíveis em scripts de teste.
- Storytelling e validações automáticas de dados em todas as páginas dos dashboards.
- Layout padronizado com navegação moderna e logo centralizado.

Se quiser adicionar mais testes, ferramentas de desenvolvimento ou novas funcionalidades, abra uma issue ou entre em contato!

---

## Licença

Distribuído sob a licença MIT — veja `LICENSE` para detalhes.
