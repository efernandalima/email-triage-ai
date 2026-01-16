from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
import logging

from app.models.schemas import AnalysisResult
from app.services.parser import extract_text_from_file
from app.services.nlp import clean_text
from app.services.classifier import classify_email

# ============================================================================
# CONFIGURAÇÃO DE LOGS
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s"
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv(find_dotenv())

# ============================================================================
# APLICAÇÃO FASTAPI
# ============================================================================
app = FastAPI(
    title="Classificador de E-mails com IA",
    description="Sistema profissional de classificação e sugestão de respostas automáticas para e-mails",
    version="1.0.0"
)

# ============================================================================
# CORS
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ARQUIVOS ESTÁTICOS (FRONTEND)
# ============================================================================
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# ============================================================================
# ROTAS
# ============================================================================
@app.get("/")
async def read_root():
    logger.info(" Página inicial acessada")
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health_check():
    logger.info(" Health check")
    return {"status": "healthy", "service": "email-classifier"}


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_email(
    file: UploadFile | None = File(default=None),
    email_text: str | None = Form(default=None),
):
    """
    Analisa um e-mail enviado via:
    - Upload de arquivo (.txt ou .pdf)
    - Texto direto informado pelo usuário
    """

    logger.info("=" * 70)

    # ------------------------------------------------------------------------
    # Validação de entrada
    # ------------------------------------------------------------------------
    if not file and not email_text:
        logger.warning(" Nenhuma entrada fornecida")
        raise HTTPException(
            status_code=400,
            detail="Envie um arquivo OU informe o texto do e-mail."
        )

    if file and email_text:
        logger.warning(" Duas entradas fornecidas ao mesmo tempo")
        raise HTTPException(
            status_code=400,
            detail="Envie apenas uma entrada: arquivo OU texto."
        )

    try:
        # --------------------------------------------------------------------
        # Extração do texto
        # --------------------------------------------------------------------
        if file:
            logger.info(f" Novo e-mail via arquivo: {file.filename}")
            raw_text = await extract_text_from_file(file)
        else:
            logger.info(" Novo e-mail via texto direto")
            raw_text = email_text.strip()

        if not raw_text:
            logger.warning(" Conteúdo vazio")
            raise HTTPException(
                status_code=400,
                detail="O conteúdo do e-mail está vazio."
            )

        logger.info(f" ✓ {len(raw_text)} caracteres recebidos")

        # --------------------------------------------------------------------
        # NLP / Limpeza de texto
        # --------------------------------------------------------------------
        logger.info(" Limpando texto com NLP...")
        cleaned_text = clean_text(raw_text)

        preview = cleaned_text[:100].replace("\n", " ")
        logger.info(f" Preview: {preview}...")

        # --------------------------------------------------------------------
        # Classificação com IA
        # --------------------------------------------------------------------
        logger.info(" Classificando com IA...")
        result = await classify_email(cleaned_text)

        logger.info(" Classificação concluída")
        logger.info(f" Categoria: {result.category}")
        logger.info(f" Confiança: {result.confidence:.1%}")
        logger.info("=" * 70)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f" Erro inesperado: {type(e).__name__}: {str(e)}")
        logger.info("=" * 70)
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar o e-mail."
        )

# ============================================================================
# EVENTOS DE CICLO DE VIDA
# ============================================================================
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 70)
    logger.info(" EMAIL CLASSIFIER AI - SERVIDOR INICIADO")
    logger.info("=" * 70)
    logger.info(" ✓ FastAPI pronto")
    logger.info(" ✓ CORS configurado")
    logger.info(" ✓ Arquivos estáticos prontos")
    logger.info(" ✓ Acesse: http://localhost:8000")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("=" * 70)
    logger.info(" Servidor encerrado")
    logger.info("=" * 70)
