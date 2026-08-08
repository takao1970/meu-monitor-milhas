import logging
import time

from config import CPM_MAXIMO_ALERTA
from database.db import init_db, promocao_ja_processada, salvar_promocao, marcar_como_enviado
from core.rss_fetcher import buscar_novos_posts
from core.web_crawler import extrair_markdown
from core.llm_parser import parsear_regulamento
from core.cpm_calculator import avaliar_promocao
from notifier.email_notifier import enviar_alerta, formatar_mensagem

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

INTERVALO_ENTRE_POSTS_SEGUNDOS = 5  # evita estourar o rate limit gratuito do Gemini


def processar_post(url: str, titulo_post: str):
    if promocao_ja_processada(url):
        logger.info("Já processado, pulando: %s", url)
        return

    time.sleep(INTERVALO_ENTRE_POSTS_SEGUNDOS)

    try:
        markdown = extrair_markdown(url)
        regulamento = parsear_regulamento(markdown)
        resultado_cpm = avaliar_promocao(regulamento, CPM_MAXIMO_ALERTA)

        promocao_id = salvar_promocao(
            url=url,
            titulo=regulamento.titulo or titulo_post,
            programa_origem=regulamento.programa_origem,
            programa_destino=regulamento.programa_destino,
            bonus_max=regulamento.percentual_bonus_maximo,
            cpm_calculado=resultado_cpm.cpm_maximo,
        )

        if resultado_cpm.viavel:
            mensagem = formatar_mensagem(
                titulo=regulamento.titulo or titulo_post,
                programa_origem=regulamento.programa_origem,
                programa_destino=regulamento.programa_destino,
                bonus_max=regulamento.percentual_bonus_maximo,
                cpm=resultado_cpm.cpm_maximo,
                url=url,
            )
            enviar_alerta(mensagem)
            marcar_como_enviado(promocao_id)
            logger.info("Alerta enviado: %s", regulamento.titulo)
        else:
            logger.info("Promoção não viável (CPM acima do teto): %s", url)

    except Exception:
        logger.exception("Falha ao processar %s", url)


def main():
    init_db()
    posts = buscar_novos_posts()
    logger.info("Encontrados %d posts novos nas últimas 24h", len(posts))

    for post in posts:
        processar_post(post.link, post.titulo)


if __name__ == "__main__":
    main()
