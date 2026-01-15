from fastapi import FastAPI, UploadFile, File, HTTPException
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
# CONFIGURAÇÃO DE LOGS DETALHADOS
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:     %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

app = FastAPI(
    title="Classificador de Emails",
    description="Sistema profissional de classificação e resposta de e-mails com IA",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

@app.get("/")
async def read_root():
    logger.info(" Página inicial acessada")
    return FileResponse("app/static/index.html")

@app.get("/health")
async def health_check():
    logger.info(" Health check")
    return {"status": "healthy", "service": "email-classifier"}

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_email(file: UploadFile = File(...)):
    """
    Analisa email e retorna classificação + resposta sugerida
    """
    logger.info("=" * 70)
    logger.info(f" NOVO EMAIL: {file.filename} ({file.content_type})")
    
    try:
        # Extrair texto
        logger.info(" Extraindo texto...")
        raw_text = await extract_text_from_file(file)
        logger.info(f"   ✓ {len(raw_text)} caracteres extraídos")
        
        if not raw_text.strip():
            logger.warning("   ⚠️  Arquivo vazio!")
            raise HTTPException(status_code=400, detail="File is empty or could not be read")

        # Limpar texto
        logger.info("🧹 Limpando texto com NLP...")
        cleaned_text = clean_text(raw_text)
        logger.info(f"   ✓ {len(cleaned_text)} caracteres após limpeza")
        
        # Preview do conteúdo
        preview = cleaned_text[:100].replace('\n', ' ')
        logger.info(f"   Preview: {preview}...")
        
        # Classificar
        logger.info(" Classificando com IA...")
        result = await classify_email(cleaned_text)
        
        # Resultado
        logger.info("✅ CONCLUÍDO!")
        logger.info(f"   Categoria: {result.category}")
        logger.info(f"   Confiança: {result.confidence:.1%}")
        logger.info(f"   Resumo: {result.summary[:80]}...")
        logger.info("=" * 70)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERRO: {type(e).__name__}: {str(e)}")
        logger.info("=" * 70)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Evento executado ao iniciar o servidor"""
    logger.info("=" * 70)
    logger.info(" EMAIL CLASSIFIER AI - SERVIDOR INICIADO")
    logger.info("=" * 70)
    logger.info("✓ FastAPI ready")
    logger.info("✓ CORS configurado")
    logger.info("✓ Arquivos estáticos prontos")
    logger.info("✓ Acesse: http://localhost:8000")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado ao encerrar o servidor"""
    logger.info("=" * 70)
    logger.info(" Servidor encerrado")
    logger.info("=" * 70)