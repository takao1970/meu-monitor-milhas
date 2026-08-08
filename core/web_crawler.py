import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


async def extrair_markdown_async(url: str, aguardar_seletor: str = None) -> str:
    """Renderiza a página (JS incluso) via Playwright/Crawl4AI e retorna o
    conteúdo textual limpo em Markdown."""
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        wait_for=f"css:{aguardar_seletor}" if aguardar_seletor else None,
        page_timeout=60000,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        resultado = await crawler.arun(url=url, config=run_config)
        if not resultado.success:
            raise RuntimeError(f"Falha ao rastrear {url}: {resultado.error_message}")
        return resultado.markdown


def extrair_markdown(url: str, aguardar_seletor: str = None) -> str:
    """Wrapper síncrono de `extrair_markdown_async` para uso em scripts simples."""
    return asyncio.run(extrair_markdown_async(url, aguardar_seletor))


if __name__ == "__main__":
    import sys

    url_teste = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    print(extrair_markdown(url_teste))
