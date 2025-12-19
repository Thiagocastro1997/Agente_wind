"""
Agente Whind - Sistema Multiagente PM + Tech Writer.

Este é o ponto de entrada principal do sistema.

COMPONENTES:
    - PM Agent: Analisa demandas e questiona viabilidade
    - Tech Writer: Gera PRDs formatados
    - Telegram Bot: Interface com o CEO

USO:
    # Instalar dependências
    uv sync
    
    # Configurar .env (copiar de .env.example)
    cp .env.example .env
    # Editar .env com suas chaves
    
    # Executar
    uv run python main.py

ARQUITETURA:
    CEO (Telegram) → Bot → Team → [PM Agent, Tech Writer] → PRD.md
"""

import sys
import logging

from config import settings

# Configura logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """
    Função principal que inicia o sistema.
    
    1. Valida configurações
    2. Inicia o bot Telegram
    
    O bot roda em loop até Ctrl+C.
    """
    print("""
╔═══════════════════════════════════════════════════════╗
║           🚀 AGENTE WHIND - MVP v0.1.0 🚀             ║
║       Sistema Multiagente PM + Tech Writer            ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    # Valida configurações
    logger.info("Validando configurações...")
    errors = settings.validate()
    
    if errors:
        logger.error("❌ Configuração inválida:")
        for error in errors:
            logger.error(f"   - {error}")
        logger.error("\n📝 Configure o arquivo .env (veja .env.example)")
        sys.exit(1)
    
    logger.info("✅ Configurações OK")
    logger.info(f"   Modelo: {settings.MODEL_ID}")
    logger.info(f"   Repo: {settings.GITHUB_REPO or 'Não configurado'}")
    logger.info(f"   PRDs: {settings.PRD_OUTPUT_DIR}")
    
    # Inicia o bot
    logger.info("\n🤖 Iniciando bot Telegram...")
    logger.info("   Pressione Ctrl+C para encerrar\n")
    
    try:
        from bot.telegram_bot import run_bot
        run_bot()
    except KeyboardInterrupt:
        logger.info("\n👋 Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
