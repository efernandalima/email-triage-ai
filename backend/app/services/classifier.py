import os
import json
from openai import AsyncOpenAI
from app.models.schemas import AnalysisResult

async def classify_email(text: str) -> AnalysisResult:
    """
    Classifies the email as Productive/Improductive and suggests a response.
    Uses OpenAI or a Mock fallback based on env config.
    """

    use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"

    if use_mock:
        return _mock_classify(text)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = AsyncOpenAI(api_key=api_key)

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional email assistant API.\n"
                        "Classify emails as Productive or Improductive and "
                        "generate a professional response.\n"
                        "Return ONLY valid JSON."
                    )
                },
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content)

        return AnalysisResult(
            category=data["category"],
            confidence=data["confidence"],
            summary=data["summary"],
            suggested_response=data["suggested_response"],
        )

    except Exception as e:
        print(f"AI Error: {e}")
        return _mock_classify(text)


def _mock_classify(text: str) -> AnalysisResult:
    """
    Simple keyword-based mock for testing without API costs.
    """
    text_lower = text.lower()
    productive_keywords = ["requisito", "erro", "bug", "projeto", "reunião", "prazo", "anexo", "dúvida", "invoice", "pagamento"]
    
    is_productive = any(word in text_lower for word in productive_keywords)
    
    category = "Productive" if is_productive else "Improductive"
    
    if category == "Productive":
        response = "Prezado(a), obrigado pelo contato. Recebemos sua solicitação e nossa equipe técnica irá analisar o caso. Retornaremos em breve."
    else:
        response = "Olá! Agradecemos a mensagem e desejamos o mesmo para você."
        
    return AnalysisResult(
        category=category,
        confidence=0.85,
        summary="Classificação simulada (Mock Mode) baseada em palavras-chave.",
        suggested_response=response
    )
