"""
Tech Writer Agent - Agente de Documentação Técnica.

Este agente é responsável por:
1. Receber o consenso entre PM e CEO
2. Gerar um PRD (Product Requirements Document) completo
3. Salvar o PRD como arquivo .md

FLUXO:
    PM passa consenso → Tech Writer gera PRD → Salva arquivo

OUTPUT:
    Arquivo markdown em output/prd/PRD_<nome>_<timestamp>.md
    
ESTRUTURA DO PRD:
    - Objetivo
    - Requisitos funcionais
    - Requisitos não-funcionais
    - User Stories
    - Critérios de aceitação
    - Análise de impacto
    - Estimativa de esforço
"""

from datetime import datetime
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from config import settings


# Template de instruções para geração de PRD
TECH_WRITER_INSTRUCTIONS = """
Você é um Tech Writer especialista em documentação técnica para desenvolvedores.

## SEU PAPEL
Transformar o consenso entre PM e CEO em um PRD (Product Requirements Document)
completo, claro e acionável para a equipe de desenvolvimento.

## ESTRUTURA DO PRD

Siga EXATAMENTE esta estrutura:

```markdown
# PRD: [Nome da Feature]

**Data:** [data atual]
**Versão:** 1.0
**Status:** Draft

## 1. Objetivo
[Descrição clara do que será implementado e por quê]

## 2. Contexto
[Background e motivação do CEO para essa demanda]

## 3. Requisitos Funcionais
- RF01: [Requisito]
- RF02: [Requisito]
...

## 4. Requisitos Não-Funcionais
- RNF01: [Performance, segurança, etc]
...

## 5. User Stories

### US01: [Título]
**Como** [persona]
**Quero** [ação]
**Para** [benefício]

**Critérios de Aceitação:**
- [ ] [Critério 1]
- [ ] [Critério 2]

## 6. Análise de Impacto
### Arquivos/Módulos Afetados
- `arquivo1.py`: [descrição da mudança]
- `arquivo2.py`: [descrição da mudança]

### Dependências
- [Dependência 1]
- [Dependência 2]

### Riscos Identificados
| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| [Risco 1] | Alta/Média/Baixa | Alto/Médio/Baixo | [Ação] |

## 7. Estimativa de Esforço
| Componente | Complexidade | Estimativa |
|------------|--------------|------------|
| [Componente 1] | Baixa/Média/Alta | [X dias] |

**Total estimado:** [X dias]

## 8. Próximos Passos
1. [ ] [Passo 1]
2. [ ] [Passo 2]
```

## REGRAS IMPORTANTES
- Use linguagem técnica precisa
- Seja específico e mensurável nos requisitos
- Inclua TODOS os critérios de aceitação
- Base as estimativas na análise do PM
- NÃO invente informações - use apenas o que foi passado pelo PM
"""


def create_tech_writer_agent() -> Agent:
    """
    Cria e retorna o agente Tech Writer configurado.
    
    O agente usa:
    - GPT-4o-mini como modelo
    - Instruções focadas em geração de PRD
    - Formato markdown estruturado
    
    Returns:
        Agent: Agente Tech Writer pronto para uso
        
    Example:
        >>> tw = create_tech_writer_agent()
        >>> response = tw.run("Contexto do PM: [...]")
        >>> print(response.content)  # PRD em markdown
    """
    agent = Agent(
        name="Tech Writer",
        role="Especialista em documentação técnica que gera PRDs completos",
        model=OpenAIChat(id=settings.MODEL_ID),
        instructions=TECH_WRITER_INSTRUCTIONS,
        markdown=True,
    )
    
    return agent


def save_prd(content: str, feature_name: str) -> Path:
    """
    Salva o PRD gerado em um arquivo markdown.
    
    Args:
        content: Conteúdo do PRD em markdown
        feature_name: Nome da feature para o arquivo
        
    Returns:
        Path: Caminho do arquivo salvo
        
    Example:
        >>> path = save_prd("# PRD...", "login_social")
        >>> print(f"Salvo em: {path}")
    """
    # Limpa o nome da feature para uso em arquivo
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in feature_name)
    safe_name = safe_name[:50]  # Limita tamanho
    
    # Gera timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Monta caminho do arquivo
    filename = f"PRD_{safe_name}_{timestamp}.md"
    filepath = settings.PRD_OUTPUT_DIR / filename
    
    # Salva o arquivo
    filepath.write_text(content, encoding="utf-8")
    
    return filepath


# Para testes diretos do módulo
if __name__ == "__main__":
    tw = create_tech_writer_agent()
    print(f"✅ Tech Writer criado: {tw.name}")
    print(f"   Output dir: {settings.PRD_OUTPUT_DIR}")
