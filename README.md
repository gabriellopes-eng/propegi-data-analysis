# PROPEGI – Dashboards e Análises de Dados (UPE)

Repositório com dashboards em **Streamlit** para visualizar os dados do **Projeto de Desenvolvimento Tecnológico** e **PROPEGI Financeiro**

---

## 📦 Módulos

- **Projeto de Desenvolvimento Tecnológico** 
- **PROPEGI Financeiro** 

---

## 📁 Estrutura

```
PROPEGI-DATA-ANALYSIS/
├─ Projeto de Desenvolvimento Tecnologico/
│  ├─ input/                              # dados brutos
│  └─ output/
│     ├─ dados_tratados.csv               # base tratada (usada pelo Streamlit)
│     └─ processar_dados_projetos.ipynb   # notebook de tratamento
│
├─ PROPEGI Financeiro/                    
│  ├─ input/
│  │  └─ Financas.json
│  └─ output/
│     ├─ dados_tratados.csv
│     └─ processar_dados_financeiro.ipynb
│
├─ Streamlit/
│  ├─ projeto.py                          # app  (Tecnológico)
│  └─ projeto_financeiro.py               # app  (Financeiro)
│
└─ README.md
```

---

## ✅ O que os dashboards entregam

### **Projeto de Desenvolvimento Tecnológico**
- Comparativo mensal — Agência × Unidade × IA-UPE (linhas + cards)  
- Projetos por Ano × Segmento (colunas empilhadas)  
- Recebimentos anuais — Agência × Unidade × IA-UPE (barras)  
- Recebimentos por ano por Setor + pizza por setor  

### **PROPEGI Financeiro** 
- Em Desenvolvimento

Ambos os apps leem apenas os CSVs em `output/`.

---

## 🧩 Requisitos

- Python **3.10+**  
- Bibliotecas:
  - `streamlit`
  - `pandas`
  - `plotly`
  - `openpyxl` (para leitura de `.xlsx` nos notebooks)

Opcional — `requirements.txt`:
```
streamlit
pandas
plotly
openpyxl
```

---

## 🚀 Como rodar

Na raiz do repositório:

### 1) (Opcional) Criar ambiente virtual

**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2) Instalar dependências

Com `requirements.txt`:
```bash
pip install -r requirements.txt
```

Sem `requirements.txt`:
```bash
pip install streamlit pandas plotly openpyxl
```

---

### 3) Garantir as bases tratadas

- **Tecnológico:**  
  `Projeto de Desenvolvimento Tecnologico/output/dados_tratados.csv`

- **Financeiro:**  
  `PROPEGI Financeiro/output/dados_tratados.csv`

Se não existirem, rode os notebooks:

- `Projeto de Desenvolvimento Tecnologico/output/processar_dados_projetos.ipynb`  
- `PROPEGI Financeiro/output/processar_dados_financeiro.ipynb`  

---

### 4) Iniciar o app

**Tecnológico (principal)**
```bash
streamlit run Streamlit/projeto.py
```

**Financeiro (opcional)**
```bash
streamlit run Streamlit/projeto_financeiro.py
```

O navegador abre automaticamente (ex.: [http://localhost:8501](http://localhost:8501)).

---

## 📊 Colunas mínimas esperadas

### **Tecnológico — dados_tratados.csv**
- Data publicação (ou equivalente p/ ano/mês)  
- Segmento  
- Status (Concluído / Em andamento / Aberto)  
- Valor agência, Valor unidade, Valor IA-UPE  

### **Financeiro — dados_tratados.csv 
- Em desenvolvimento

---

## 🔄 Atualizar dados

1. Coloque os brutos em `input/`.  
2. Rode o notebook para gerar `dados_tratados.csv` em `output/`.  
3. Recarregue o Streamlit (ou reinicie `streamlit run`).  

---

### Boas práticas
- Manter nomes de colunas estáveis.  
- Documentar mudanças nos notebooks (changelog).  
- Versionar apenas código e CSVs tratados não sensíveis.  

---

## 🤝 Contribuição

1. Criar uma branch:
```bash
git checkout -b feat/minha-melhoria
```
2. Fazer commits pequenos e objetivos.  
3. Abrir PR com descrição e prints dos gráficos (quando possível).  
