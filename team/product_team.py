"""
Product Team - Coordenador de Agentes.

Este módulo cria o Team que coordena PM e Tech Writer.

FLUXO DO TEAM:
    1. CEO envia mensagem
    2. Team delega para PM Agent
    3. PM analisa e questiona CEO
    4. Quando há consenso, PM passa para Tech Writer
    5. Tech Writer gera PRD
    6. Team retorna PRD para o CEO

PERSISTÊNCIA:
    - SQLite para sessões (histórico de conversas)
    - SQLite para memória (informações importantes entre sessões)

USO:
    from team.product_team import create_product_team
    
    team = create_product_team()
    response = team.run("Quero adicionar login social")
"""

from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

from config import settings
from agents.pm_agent import create_pm_agent
from agents.tech_writer import create_tech_writer_agent


# Instruções para o Team Leader (coordenador)
TEAM_INSTRUCTIONS = """
Você É o PM falando diretamente com o CEO. Responda SEMPRE em primeira pessoa,
de forma natural e conversacional, como se fosse uma conversa entre colegas.

## REGRAS DE COMUNICAÇÃO

1. NUNCA diga "o PM precisa...", "vou delegar para...", "o agente vai..."
2. SEMPRE fale como se VOCÊ fosse o PM: "eu preciso saber...", "vou analisar..."
3. Seja objetivo e natural, sem formalidades excessivas
4. Use linguagem coloquial profissional
5. LEMBRE das conversas anteriores - o CEO pode fazer referência a demandas passadas

## EXEMPLO DE COMO RESPONDER

❌ ERRADO: "Vou delegar para o PM Agent analisar. O PM precisa de informações..."
✅ CERTO: "Beleza, deixa eu dar uma olhada nisso. Só preciso entender melhor..."

❌ ERRADO: "Para iniciarmos, preciso que você forneça detalhes..."
✅ CERTO: "Me conta mais sobre isso. Qual o contexto?"

## FLUXO

1. Quando o CEO pede algo, analise e pergunte o que precisar
2. Quando tiver todas as infos, gere o PRD
3. Sempre lembre do histórico da conversa

## MEMÓRIA

Você tem acesso ao histórico. Se o CEO mencionar "a demanda anterior" ou 
"o que conversamos", consulte a memória e continue de onde pararam.
"""


def create_product_team() -> Team:
    """
    Cria e retorna o Team de produto configurado.
    
    O Team coordena:
    - PM Agent: análise e questionamento
    - Tech Writer: geração de PRD
    
    Configurações:
    - Modelo: gpt-4o-mini (via .env)
    - Storage: SQLite para memória
    - Show members: True (mostra quem respondeu)
    
    Returns:
        Team: Team pronto para uso
        
    Example:
        >>> team = create_product_team()
        >>> response = team.run("Quero adicionar login social")
        >>> print(response.content)
    """
    # Cria os agentes
    pm_agent = create_pm_agent()
    tech_writer = create_tech_writer_agent()
    
    # Configura SQLite para persistência
    db = SqliteDb(
        db_file=settings.SQLITE_PATH,
    )
    
    # Cria o Team
    team = Team(
        name="Product Team",
        members=[pm_agent, tech_writer],
        model=OpenAIChat(id=settings.MODEL_ID),
        instructions=TEAM_INSTRUCTIONS,
        db=db,
        # Habilita memória para lembrar decisões anteriores
        enable_user_memories=True,
        markdown=True,
        # Mostra qual agente respondeu
        show_members_responses=True,
    )
    
    return team


# Para testes diretos do módulo
if __name__ == "__main__":
    team = create_product_team()
    print(f"✅ Product Team criado: {team.name}")
    print(f"   Membros: {[m.name for m in team.members]}")
    print(f"   DB: {settings.SQLITE_PATH}")
