# meu-monitor-milhas

Monitor pessoal e privado de promoções de milhas: coleta feeds RSS, faz scraping
do regulamento, extrai dados estruturados via LLM, calcula CPM e alerta por e-mail.

## Pipeline (main.py)
`rss_fetcher` (posts 24h) → `web_crawler` (URL → markdown) → `llm_parser`
(markdown → `PromocaoRegulamento`) → `cpm_calculator` (CPM x teto) → `db`
(dedup por hash da URL) → `email_notifier` (alerta se viável).

## Módulos
- `config.py` — lê `.env`. Fonte única de configuração; não hardcode valores alhures.
- `database/db.py` — SQLite (`milhas_monitor.db`), tabela `promocoes`. Dedup via
  `promocao_ja_processada(url)` antes de qualquer scraping/LLM (evita custo de API).
- `core/rss_fetcher.py` — `buscar_novos_posts()` → `list[PostRSS]`.
- `core/web_crawler.py` — `extrair_markdown(url)` (Crawl4AI+Playwright, headless).
- `core/llm_parser.py` — `parsear_regulamento(markdown)` → `PromocaoRegulamento`
  (Pydantic, via Claude — `client.messages.parse(output_format=...)`; modelo em
  `config.CLAUDE_MODEL`, `claude-haiku-4-5` por padrão — suficiente e barato para
  extração estruturada de texto curto).
- `core/cpm_calculator.py` — `avaliar_promocao(regulamento)` → `ResultadoCPM`.
  CPM = custo por 1.000 pontos no destino; menor é melhor. Teto em `CPM_MAXIMO_ALERTA`.
- `notifier/email_notifier.py` — `enviar_alerta(mensagem)` via SMTP do Gmail
  (`EMAIL_REMETENTE` precisa de senha de app, não a senha normal da conta).

## Comandos
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install chromium
crawl4ai-setup
python database/db.py          # inicializa o banco
python main.py                 # roda o pipeline uma vez
```

## Convenções
- Sem testes automatizados ainda; validar manualmente rodando `main.py`.
- Segredos só em `.env` (nunca commitar); `.env.example` documenta as chaves.
- Todo módulo em `core/`/`notifier/`/`database/` importa `config` via
  `sys.path.append` do diretório pai — manter esse padrão em novos arquivos.
- `sqlite3` é da stdlib, não entra em `requirements.txt`.
