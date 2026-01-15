# 📧 Email Triage AI — Classificador de E-mails com Inteligência Artificial

Solução web desenvolvida para **automatizar a leitura, classificação e resposta de e-mails** utilizando **Inteligência Artificial**, com foco em **ganho de produtividade** para equipes que lidam com alto volume de mensagens diariamente.

Este projeto foi desenvolvido como parte de um **desafio técnico**, simulando um cenário real de uma **grande empresa do setor financeiro**.

---

## 🎯 Objetivo do Projeto

Automatizar o processo de triagem de e-mails, classificando-os em categorias pré-definidas e sugerindo respostas automáticas adequadas ao contexto da mensagem, reduzindo o trabalho manual e liberando tempo da equipe para atividades mais estratégicas.

---

## 🧠 Funcionalidades

- 📂 Upload de e-mails nos formatos **.txt** e **.pdf**
- 🧾 Extração automática do texto dos arquivos
- 🧹 Pré-processamento de texto (NLP básico)
- 🤖 Classificação automática do e-mail em:
  - **Produtivo** — requer ação ou resposta
  - **Improdutivo** — não requer ação imediata
- ✍️ Geração de **resposta automática sugerida**
- 🌐 Interface web moderna, intuitiva e responsiva
- 🧪 **Modo Mock AI** para testes e demonstração sem custo de API

---

## 🖥️ Interface Web

A aplicação disponibiliza uma interface web simples e amigável, permitindo:

- Arrastar e soltar arquivos de e-mail
- Visualizar a classificação atribuída ao conteúdo
- Visualizar a resposta automática sugerida pela IA

### Tecnologias do Frontend

- HTML5
- CSS3
- JavaScript (Vanilla)

---

## ⚙️ Tecnologias Utilizadas

### Backend

- **Python 3.11**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **python-dotenv**
- **PyPDF**
- **OpenAI API**
- **httpx**

### Frontend

- HTML5
- CSS3
- JavaScript

---

## 📁 Estrutura do Projeto

```text
email-triage-ai/
├── backend/
│   └── app/
│       ├── models/
│       │   └── schemas.py
│       ├── services/
│       │   ├── parser.py
│       │   ├── nlp.py
│       │   └── classifier.py
│       ├── static/
│       │   ├── index.html
│       │   ├── style.css
│       │   └── script.js
│       └── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Como Executar Localmente

### 1️⃣ Clonar o repositório

```bash
git clone https://github.com/efernandalima/email-triage-ai.git
cd email-triage-ai
```

### 2️⃣ Criar e ativar o ambiente virtual

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3️⃣ Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
USE_MOCK_AI=true
```

🔹 `USE_MOCK_AI=true` permite executar o projeto **sem consumir a API da OpenAI**  
🔹 Para usar a IA real, altere para `false`

### 5️⃣ Executar o servidor

```bash
cd backend
uvicorn app.main:app --reload
```

---

## 🌐 Acesso à Aplicação

- **Interface Web:** http://127.0.0.1:8000
- **Documentação da API (Swagger):** http://127.0.0.1:8000/docs

---

## 🧪 Exemplo de Uso

1. Acesse a interface web
2. Faça upload de um arquivo `.txt` ou `.pdf`
3. Clique em **Analisar e-mail**
4. Visualize:
   - Categoria do e-mail (Produtivo / Improdutivo)
   - Resposta automática sugerida

---

## 📝 Observações Técnicas

- Projeto organizado com **separação clara de responsabilidades**
- Uso de **fallback automático (Mock AI)** em caso de falha ou ausência da API
- Estrutura pensada para **facilidade de manutenção e escalabilidade**
- Código limpo, modular e documentado

---

## 👤 Autora

**Fernanda Lima**  
📧 Projeto desenvolvido para **desafio técnico — AutoU**

---
