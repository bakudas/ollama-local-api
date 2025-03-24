from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx
from typing import List, Optional
import logging
import json

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ollama Local API",
    description="API para interagir com modelos de linguagem locais via Ollama",
    version="1.0.0"
)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:14b"  # Modelo padrão

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="O prompt para enviar ao modelo")
    model: Optional[str] = Field(None, description="Nome do modelo a ser usado (opcional)")

class LLMResponse(BaseModel):
    response: str = Field(..., description="Resposta do modelo")

class ModelInfo(BaseModel):
    name: str
    size: int
    digest: str
    modified_at: str

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """
    Lista todos os modelos disponíveis no Ollama
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return models
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao listar modelos: {str(e)}")

@app.post("/ask", response_model=LLMResponse)
async def ask_ollama(data: PromptRequest):
    """
    Envia um prompt para o modelo e retorna sua resposta
    """
    model = data.model or OLLAMA_MODEL
    payload = {
        "model": model,
        "prompt": data.prompt,
        "stream": False
    }

    logger.debug(f"Enviando requisição para o modelo {model}")
    logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
            logger.debug(f"Status code da resposta: {response.status_code}")
            logger.debug(f"Headers da resposta: {response.headers}")

            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"Erro na resposta do Ollama: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erro na resposta do Ollama: {error_detail}"
                )

            try:
                json_resp = response.json()
                logger.debug(f"Resposta JSON: {json.dumps(json_resp, ensure_ascii=False)}")
                return {"response": json_resp.get("response", "")}
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar JSON: {str(e)}")
                logger.error(f"Conteúdo da resposta: {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail="Erro ao processar resposta do Ollama"
                )

        except httpx.ConnectError as e:
            logger.error(f"Erro de conexão com Ollama: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail="Não foi possível conectar ao Ollama. Verifique se o serviço está rodando."
            )
        except httpx.TimeoutException as e:
            logger.error(f"Timeout na requisição: {str(e)}")
            raise HTTPException(
                status_code=504,
                detail="A requisição excedeu o tempo limite"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Erro HTTP: {str(e)}")
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Modelo '{model}' não encontrado. Verifique se o modelo está instalado."
                )
            raise HTTPException(
                status_code=500,
                detail=f"Erro na comunicação com Ollama: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno: {str(e)}"
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
