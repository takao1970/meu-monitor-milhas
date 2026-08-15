import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Remove menu, cookie banner, sidebar, rodapé etc. antes de enviar à LLM —
# reduz o texto de ~29.000 para poucos milhares de caracteres, cortando
# diretamente o custo por chamada.
FILTRO_CONTEUDO = PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0)
GERADOR_MARKDOWN = DefaultMarkdownGenerator(content_filter=FILTRO_CONTEUDO)


async def extrair_markdown_async(url: str, aguardar_seletor: str = None) -> str:
    """Renderiza a página (JS incluso) via Playwright/Crawl4AI e retorna o
    conteúdo textual relevante em Markdown (filtrado, sem menu/anúncios/rodapé)."""
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        wait_for=f"css:{aguardar_seletor}" if aguardar_seletor else None,
        page_timeout=60000,
        markdown_generator=GERADOR_MARKDOWN,
        remove_overlay_elements=True,
        remove_consent_popups=True,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        resultado = await crawler.arun(url=url, config=run_config)
        if not resultado.success:
            raise RuntimeError(f"Falha ao rastrear {url}: {resultado.error_message}")
        # fit_markdown é o conteúdo filtrado; cai para o markdown bruto se o
        # filtro descartar tudo (páginas com estrutura incomum).
        return resultado.markdown.fit_markdown or resultado.markdown.raw_markdown


def extrair_markdown(url: str, aguardar_seletor: str = None) -> str:
    """Wrapper síncrono de `extrair_markdown_async` para uso em scripts simples."""
    return asyncio.run(extrair_markdown_async(url, aguardar_seletor))


if __name__ == "__main__":
    import sys

    url_teste = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(extrair_markdown(url_teste))
