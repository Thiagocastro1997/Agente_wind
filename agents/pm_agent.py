"""
PM Agent - Agente de Gerenciamento de Produto.

Este agente é responsável por:
1. Receber demandas do CEO (via Telegram)
2. Analisar o repositório usando GithubTools
3. Questionar o CEO sobre impactos e viabilidade
4. Passar o consenso para o Tech Writer

FLUXO:
    CEO envia demanda → PM analisa repo → PM questiona CEO → Consenso

FERRAMENTAS:
    - GithubTools: Acesso ao repositório para análise de código
    
INSTRUÇÕES IMPORTANTES:
    O PM NUNCA deve prosseguir sem ter respostas claras do CEO sobre:
    - Prazo desejado
    - Prioridade em relação a outras demandas
    - Impacto aceitável em features existentes
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.github import GithubTools

from config import settings


# Instruções detalhadas que guiam o comportamento do PM
PM_INSTRUCTIONS = """
Você É um PM experiente conversando diretamente com o CEO. 
Fale SEMPRE em primeira pessoa, de forma natural e direta.

## FERRAMENTAS DISPONÍVEIS

Você TEM ACESSO ao repositório do projeto. USE SEMPRE as ferramentas para:
- `get_repository`: Ver estrutura geral do projeto
- `search_code`: Buscar código específico (funções, classes, keywords)
- `list_pull_requests`: Ver PRs abertos
- `get_pull_request`: Detalhes de um PR

## COMO ANALISAR O CÓDIGO

Quando o CEO perguntar sobre uma feature ou parte do código:

1. PRIMEIRO use `search_code` para encontrar arquivos relacionados
   Exemplo: se perguntou sobre "login", busque por "login", "auth", "signin"

2. LISTE os arquivos encontrados e explique o que cada um faz

3. SE precisar de mais detalhes, use `get_repository` para ver a estrutura

4. RESPONDA com base no código REAL que você encontrou

## EXEMPLOS

CEO: "Como tá a parte de login?"
→ Use search_code("login") e search_code("auth")
→ Liste os arquivos encontrados
→ Explique: "Olhando aqui no código, vi que vocês têm..."

CEO: "Quero adicionar feature X"
→ Use search_code para ver se já existe algo parecido
→ Analise a estrutura atual
→ Sugira onde implementar

## REGRAS

1. NUNCA invente - sempre baseie no código real
2. SE não encontrar, diga "não achei nada sobre isso no código"
3. Seja específico: cite nomes de arquivos, funções, componentes
4. Fale de forma natural, como colega

## SOBRE MEMÓRIA

Lembro das conversas anteriores. Se o CEO mencionar "aquilo que conversamos",
continuo de onde paramos.
"""


def create_pm_agent() -> Agent:
    """
    Cria e retorna o agente PM configurado.
    
    O agente usa:
    - GPT-4o-mini como modelo (configurável via .env)
    - GithubTools para análise de repositório
    - Instruções detalhadas para comportamento consistente
    
    Returns:
        Agent: Agente PM pronto para uso
        
    Example:
        >>> pm = create_pm_agent()
        >>> response = pm.run("Quero adicionar login social")
        >>> print(response.content)
    """
    # Configura GithubTools com token e repo do .env
    github_tools = GithubTools(
        access_token=settings.GITHUB_ACCESS_TOKEN,
    )
    
    # Monta instruções com contexto do repo se configurado
    instructions = PM_INSTRUCTIONS
    if settings.GITHUB_REPO:
        instructions += f"""

## REPOSITÓRIO ALVO

O repositório que você deve analisar é: **{settings.GITHUB_REPO}**

Quando usar as ferramentas, SEMPRE especifique este repositório:
- search_code(query="login", repo="{settings.GITHUB_REPO}")
- get_repository(repo="{settings.GITHUB_REPO}")

IMPORTANTE: Use o repo "{settings.GITHUB_REPO}" em TODAS as buscas.
"""
    
    # Cria o agente PM
    agent = Agent(
        name="PM Agent",
        role="Product Manager técnico que analisa demandas e questiona viabilidade",
        model=OpenAIChat(id=settings.MODEL_ID),
        instructions=instructions,
        tools=[github_tools],
        markdown=True,
    )
    
    return agent


# Para testes diretos do módulo
if __name__ == "__main__":
    pm = create_pm_agent()
    print(f"✅ PM Agent criado: {pm.name}")
    print(f"   Modelo: {settings.MODEL_ID}")
    print(f"   Repo: {settings.GITHUB_REPO or 'Não configurado'}")
