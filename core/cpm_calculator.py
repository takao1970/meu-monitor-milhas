import sys
import os
from dataclasses import dataclass
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CPM_MAXIMO_ALERTA
from core.llm_parser import PromocaoRegulamento


@dataclass
class ResultadoCPM:
    cpm_padrao: Optional[float]  # R$ por 1.000 pontos no destino, com bônus padrão
    cpm_maximo: Optional[float]  # R$ por 1.000 pontos no destino, com bônus máximo
    viavel: bool


def calcular_cpm(custo_por_mil_origem: float, percentual_bonus: float) -> float:
    """CPM = custo para obter 1.000 pontos no programa de destino, considerando
    o bônus de transferência. Quanto menor, melhor o negócio."""
    pontos_destino_por_mil_origem = 1000 * (1 + percentual_bonus / 100)
    return (custo_por_mil_origem / pontos_destino_por_mil_origem) * 1000


def avaliar_promocao(
    regulamento: PromocaoRegulamento, cpm_maximo_alerta: float = CPM_MAXIMO_ALERTA
) -> ResultadoCPM:
    """Calcula o CPM da promoção (padrão e máximo) e indica se é viável frente
    ao teto configurado pelo usuário."""
    custo = regulamento.custo_compra_ponto_origem_por_mil

    if custo is None:
        return ResultadoCPM(cpm_padrao=None, cpm_maximo=None, viavel=False)

    cpm_padrao = calcular_cpm(custo, regulamento.percentual_bonus_padrao)
    cpm_maximo = calcular_cpm(custo, regulamento.percentual_bonus_maximo)

    viavel = cpm_maximo <= cpm_maximo_alerta

    return ResultadoCPM(cpm_padrao=cpm_padrao, cpm_maximo=cpm_maximo, viavel=viavel)
