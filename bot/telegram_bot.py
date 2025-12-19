"""
Telegram Bot - Interface conversacional simplificada.

Usa o PM Agent diretamente (sem Team) para garantir
que as ferramentas de GitHub sejam usadas corretamente.
"""

import logging
import io

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import AsyncOpenAI

from config import settings
from agents.pm_agent import create_pm_agent
from agents.tech_writer import create_tech_writer_agent, save_prd
from tools.audio import transcribe_audio_bytes

# Configura logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Agentes e cliente (singletons)
_pm_agent = None
_tech_writer = None
_openai_client = None


def get_pm_agent():
    """Retorna o PM Agent (singleton)."""
    global _pm_agent
    if _pm_agent is None:
        logger.info("Criando PM Agent...")
        _pm_agent = create_pm_agent()
    return _pm_agent


def get_tech_writer():
    """Retorna o Tech Writer (singleton)."""
    global _tech_writer
    if _tech_writer is None:
        logger.info("Criando Tech Writer...")
        _tech_writer = create_tech_writer_agent()
    return _tech_writer


def get_openai_client():
    """Retorna cliente OpenAI para TTS."""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


async def text_to_speech(text: str) -> bytes:
    """Converte texto para áudio usando OpenAI TTS."""
    client = get_openai_client()
    
    # Limita texto e limpa formatação
    clean_text = text[:4000].replace("**", "").replace("##", "").replace("# ", "")
    
    response = await client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=clean_text,
    )
    
    return response.content


# ============================================
# HANDLERS
# ============================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para /start."""
    welcome = "Oi! Sou seu PM. Me conta o que você precisa que eu analiso o projeto e a gente conversa."
    
    try:
        audio_bytes = await text_to_speech(welcome)
        await update.message.reply_voice(io.BytesIO(audio_bytes))
    except Exception as e:
        logger.error(f"Erro TTS: {e}")
        await update.message.reply_text(welcome)


async def process_message(update: Update, user_message: str) -> None:
    """Processa mensagem usando PM Agent diretamente."""
    user_id = update.effective_user.id
    
    logger.info(f"[{user_id}] Mensagem: {user_message[:50]}...")
    
    try:
        # Usa PM Agent diretamente
        pm = get_pm_agent()
        
        logger.info(f"[{user_id}] Chamando PM Agent...")
        response = pm.run(
            user_message,
            session_id=f"telegram_{user_id}",
        )
        
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        logger.info(f"[{user_id}] Resposta: {response_text[:100]}...")
        
        # Verifica se precisa gerar PRD
        if "gerar prd" in user_message.lower() or "cria o prd" in user_message.lower():
            tw = get_tech_writer()
            prd_response = tw.run(f"Gere um PRD baseado neste contexto:\n\n{response_text}")
            prd_text = prd_response.content if hasattr(prd_response, 'content') else str(prd_response)
            
            # Salva PRD
            prd_path = save_prd(prd_text, "feature")
            await update.message.reply_document(
                document=open(prd_path, 'rb'),
                filename=prd_path.name,
            )
            response_text = "Pronto, gerei o PRD. Dá uma olhada no arquivo."
        
        # Responde em áudio
        await send_audio_response(update, response_text)
        
    except Exception as e:
        logger.error(f"[{user_id}] Erro: {e}", exc_info=True)
        await update.message.reply_text(f"Desculpa, deu um erro aqui: {str(e)[:100]}")


async def send_audio_response(update: Update, text: str) -> None:
    """Envia resposta APENAS em áudio."""
    try:
        audio_bytes = await text_to_speech(text)
        await update.message.reply_voice(io.BytesIO(audio_bytes))
    except Exception as e:
        logger.error(f"Erro TTS: {e}")
        # Fallback para texto
        await update.message.reply_text(text[:2000])


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para texto."""
    await process_message(update, update.message.text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para áudio - transcreve silenciosamente."""
    try:
        if update.message.voice:
            file = await update.message.voice.get_file()
            filename = "voice.ogg"
        elif update.message.audio:
            file = await update.message.audio.get_file()
            filename = update.message.audio.file_name or "audio.mp3"
        else:
            return
        
        audio_bytes = await file.download_as_bytearray()
        transcription = await transcribe_audio_bytes(bytes(audio_bytes), filename)
        
        logger.info(f"Transcrição: {transcription[:50]}...")
        
        await process_message(update, transcription)
        
    except Exception as e:
        logger.error(f"Erro áudio: {e}")
        await update.message.reply_text("Não consegui entender o áudio. Pode repetir?")


# ============================================
# INICIALIZAÇÃO
# ============================================

def run_bot() -> None:
    """Inicia o bot."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN não configurado")
    
    logger.info("Iniciando bot...")
    logger.info(f"  Repo: {settings.GITHUB_REPO}")
    
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    
    logger.info("Bot rodando!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_bot()
