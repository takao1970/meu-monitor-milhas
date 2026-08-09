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
- `gerar_dashboard.py` — lê `listar_promocoes()` do banco e gera `docs/index.html`
  (painel estático, ordenado por CPM crescente). Publicado via GitHub Pages
  (branch `main`, pasta `/docs`) — link é público, mas não listado em lugar nenhum.

## Automação (GitHub Actions)
`.github/workflows/monitor.yml` roda `main.py` + `gerar_dashboard.py` todo dia
às 8h (horário de Brasília) e às execuções manuais (`workflow_dispatch`), depois
commita `milhas_monitor.db` e `docs/index.html` de volta no repositório.
- Segredos (`ANTHROPIC_API_KEY`, `EMAIL_REMETENTE`, `EMAIL_SENHA_APP`,
  `EMAIL_DESTINATARIO`) ficam em **Settings → Secrets and variables → Actions → Secrets**.
- Configurações ajustáveis (`CPM_MAXIMO_ALERTA`, `RSS_FEEDS`) ficam em
  **Settings → Secrets and variables → Actions → Variables** — editáveis pelo
  site do GitHub (celular ou notebook) sem tocar em código.

## Comandos
```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install chromium
crawl4ai-setup
python database/db.py          # inicializa/migra o banco
python main.py                 # roda o pipeline uma vez
python gerar_dashboard.py      # regenera docs/index.html a partir do banco atual
```

## Convenções
- Sem testes automatizados ainda; validar manualmente rodando `main.py`.
- Segredos só em `.env` local ou GitHub Secrets (nunca commitar); `.env.example`
  documenta as chaves.
- Todo módulo em `core/`/`notifier/`/`database/` importa `config` via
  `sys.path.append` do diretório pai — manter esse padrão em novos arquivos.
- `sqlite3` é da stdlib, não entra em `requirements.txt`.
- Mudanças de schema em `database/db.py` precisam de migração idempotente em
  `init_db()` (ver padrão do `MIGRACAO_ADICIONAR_URL`) — o banco de produção
  vive commitado no repositório, não pode ser recriado do zero.
