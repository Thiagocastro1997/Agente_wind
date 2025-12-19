"""
Configuração centralizada do sistema.

Este módulo carrega variáveis de ambiente e define constantes
usadas em todo o projeto.

USO:
    from config import settings
    print(settings.MODEL_ID)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env do diretório raiz
load_dotenv()

# ============================================
# DIRETÓRIOS
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output" / "prd"

# Cria diretórios se não existem
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    """
    Configurações carregadas do ambiente.
    
    Todas as variáveis sensíveis vêm do .env para segurança.
    """
    
    # APIs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GITHUB_ACCESS_TOKEN: str = os.getenv("GITHUB_ACCESS_TOKEN", "")
    
    # Repositório alvo (formato: owner/repo)
    GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
    
    # Modelo LLM
    MODEL_ID: str = os.getenv("MODEL_ID", "gpt-4o-mini")
    
    # Caminhos
    SQLITE_PATH: str = str(DATA_DIR / "memory.db")
    PRD_OUTPUT_DIR: Path = OUTPUT_DIR
    
    def validate(self) -> list[str]:
        """
        Valida se todas as configurações obrigatórias estão presentes.
        
        Returns:
            Lista de erros (vazia se tudo OK)
        """
        errors = []
        
        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY não configurada")
        if not self.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN não configurado")
        if not self.GITHUB_ACCESS_TOKEN:
            errors.append("GITHUB_ACCESS_TOKEN não configurado")
            
        return errors


# Instância global de configurações
settings = Settings()
