# Ollama Local API

API REST para interagir com modelos de linguagem locais via Ollama.

## Requisitos

- Python 3.7+
- Ollama instalado e rodando localmente
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone este repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Certifique-se de que o Ollama está rodando localmente
2. Inicie a API:
```bash
python main.py
```

A API estará disponível em `http://localhost:8000`

## Endpoints

### GET /models
Lista todos os modelos disponíveis no Ollama.

### POST /ask
Envia um prompt para o modelo e retorna sua resposta.

Exemplo de requisição:
```json
{
    "prompt": "Olá, como você está?",
    "model": "deepseek-r1:14b"  // opcional
}
```

## Documentação da API

A documentação interativa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
