import sys
import os
from typing import Optional

import anthropic
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

MAX_CARACTERES_MARKDOWN = 12000  # rede de segurança contra páginas fora do padrão


class PromocaoRegulamento(BaseModel):
    titulo: str
    programa_origem: str  # Ex: Livelo, Esfera, Banco do Brasil
    programa_destino: str  # Ex: Smiles, LATAM Pass, Azul Fidelidade
    percentual_bonus_padrao: float  # Ex: 50.0
    percentual_bonus_maximo: float  # Ex: 100.0
    requisito_bonus_maximo: Optional[str]  # Ex: Assinante do Clube Smiles
    custo_compra_ponto_origem_por_mil: Optional[float]  # Custo de comprar 1.000 pontos com desconto, se houver
    permite_parcelamento: bool
    data_limite: Optional[str]


PROMPT_SISTEMA = """Você é um extrator de dados de regulamentos de promoções de \
transferência bonificada de pontos/milhas de programas de fidelidade brasileiros. \
Leia o conteúdo em Markdown fornecido e extraia os dados estruturados solicitados. \
Se um campo não estiver explícito no texto, retorne null (ou 0.0 quando o campo for \
numérico obrigatório e não houver bônus aplicável). Não invente informações."""


class RelevanciaTitulo(BaseModel):
    relevante: bool


PROMPT_CLASSIFICACAO = """Classifique se o título de post abaixo é sobre uma \
promoção de TRANSFERÊNCIA BONIFICADA DE PONTOS/MILHAS entre programas de \
fidelidade (ex: "Livelo transfira para Smiles com 100% de bônus", "Azul \
Fidelidade para Inter Loop"). NÃO é relevante: notícias gerais, venda de \
passagem aérea, cupom de loja, "ganhe pontos comprando em X", dicas de \
viagem, hotéis, vídeos, produtos. Responda apenas com base no título."""


def eh_relevante(titulo: str) -> bool:
    """Classificação barata (só o título) para decidir se vale a pena rastrear
    a página inteira e gastar tokens com a extração completa."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    resposta = client.messages.parse(
        model=CLAUDE_MODEL,
        max_tokens=16,
        system=PROMPT_CLASSIFICACAO,
        messages=[{"role": "user", "content": titulo}],
        output_format=RelevanciaTitulo,
    )

    return resposta.parsed_output.relevante


def parsear_regulamento(markdown_conteudo: str) -> PromocaoRegulamento:
    """Envia o Markdown da promoção à Claude e retorna os dados estruturados
    validados via Pydantic."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    markdown_conteudo = markdown_conteudo[:MAX_CARACTERES_MARKDOWN]

    resposta = client.messages.parse(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=PROMPT_SISTEMA,
        messages=[
            {"role": "user", "content": f"--- CONTEÚDO DA PÁGINA ---\n{markdown_conteudo}"},
        ],
        output_format=PromocaoRegulamento,
    )

    return resposta.parsed_output


if __name__ == "__main__":
    exemplo = """
    # Livelo: transfira pontos para Smiles com até 100% de bônus
    Assinantes do Clube Smiles ganham 100% de bônus. Demais clientes, 80%.
    Promoção válida até 31/12/2026. Parcelamento não disponível.
    """
    print(parsear_regulamento(exemplo).model_dump_json(indent=2))
