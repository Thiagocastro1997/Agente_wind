"""
Audio Tool - Transcrição de áudio via OpenAI Whisper API.

Este módulo fornece funções para transcrever áudio usando a API Whisper.

FORMATOS SUPORTADOS:
    - mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg

USO:
    from tools.audio import transcribe_audio
    
    text = await transcribe_audio("audio.ogg")
    print(text)

NOTA:
    Usa a API da OpenAI diretamente, sem dependências pesadas.
    Custo: ~$0.006/minuto de áudio.
"""

from pathlib import Path
from openai import AsyncOpenAI

from config import settings


# Cliente OpenAI async para transcrições
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """
    Retorna o cliente OpenAI (singleton).
    
    Cria o cliente apenas uma vez e reutiliza.
    """
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def transcribe_audio(file_path: str | Path) -> str:
    """
    Transcreve um arquivo de áudio para texto usando Whisper API.
    
    Args:
        file_path: Caminho para o arquivo de áudio
        
    Returns:
        str: Texto transcrito
        
    Raises:
        FileNotFoundError: Se o arquivo não existir
        OpenAIError: Se houver erro na API
        
    Example:
        >>> text = await transcribe_audio("mensagem.ogg")
        >>> print(f"CEO disse: {text}")
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    
    client = _get_client()
    
    # Abre o arquivo e envia para a API
    with open(path, "rb") as audio_file:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pt",  # Português
            response_format="text",
        )
    
    return response


async def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "audio.ogg") -> str:
    """
    Transcreve bytes de áudio para texto usando Whisper API.
    
    Útil quando o áudio vem diretamente do Telegram (bytes em memória).
    
    Args:
        audio_bytes: Bytes do arquivo de áudio
        filename: Nome do arquivo (para inferir formato)
        
    Returns:
        str: Texto transcrito
        
    Example:
        >>> audio = await bot.download_file(file_id)
        >>> text = await transcribe_audio_bytes(audio, "voice.ogg")
    """
    import io
    
    client = _get_client()
    
    # Cria um file-like object dos bytes
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename  # OpenAI precisa do nome para inferir formato
    
    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="pt",
        response_format="text",
    )
    
    return response


# Para testes diretos do módulo
if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("✅ Audio tool carregado")
        print(f"   API Key: {'Configurada' if settings.OPENAI_API_KEY else 'NÃO configurada'}")
    
    asyncio.run(test())
