import html
import sys
import os
from datetime import datetime, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import CPM_MAXIMO_ALERTA
from database.db import init_db, listar_promocoes

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "index.html")


def status_promocao(cpm: float) -> tuple[str, str, str]:
    """Retorna (texto, classe_css) para o status de uma promoção."""
    if cpm is None:
        return "— sem custo de compra", "neutro"
    if cpm <= CPM_MAXIMO_ALERTA:
        return "✅ Viável", "viavel"
    return "⚠️ CPM alto", "alto"


def formatar_data(data_iso: str) -> str:
    try:
        dt = datetime.fromisoformat(data_iso)
        return dt.strftime("%d/%m/%Y %H:%M UTC")
    except (ValueError, TypeError):
        return data_iso or ""


def gerar_linha_tabela(promocao: dict) -> str:
    cpm = promocao["cpm_calculado"]
    status_texto, status_classe = status_promocao(cpm)
    cpm_texto = f"R$ {cpm:.2f}" if cpm is not None else "—"
    titulo = html.escape(promocao["titulo"] or "")
    origem = html.escape(promocao["programa_origem"] or "—")
    destino = html.escape(promocao["programa_destino"] or "—")
    bonus = f"{promocao['bonus_max']:.0f}%" if promocao["bonus_max"] is not None else "—"
    url = html.escape(promocao["url"] or "#")
    data = formatar_data(promocao["data_descoberta"])

    titulo_html = f'<a href="{url}" target="_blank" rel="noopener">{titulo}</a>' if promocao["url"] else titulo

    return f"""
    <tr class="linha-{status_classe}">
      <td class="status" data-rotulo="Status"><span class="badge badge-{status_classe}">{status_texto}</span></td>
      <td class="cpm" data-rotulo="CPM">{cpm_texto}</td>
      <td data-rotulo="Promoção">{titulo_html}</td>
      <td data-rotulo="De → Para">{origem} → {destino}</td>
      <td data-rotulo="Bônus Máx">{bonus}</td>
      <td class="data" data-rotulo="Descoberto em">{data}</td>
    </tr>"""


def gerar_html(promocoes: list[dict]) -> str:
    linhas = "\n".join(gerar_linha_tabela(p) for p in promocoes)
    total = len(promocoes)
    viaveis = sum(1 for p in promocoes if p["cpm_calculado"] is not None and p["cpm_calculado"] <= CPM_MAXIMO_ALERTA)
    atualizado_em = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Monitor de Milhas</title>
<style>
  :root {{
    color-scheme: light dark;
    --bg: #0f1115;
    --card: #171a21;
    --text: #e6e8eb;
    --muted: #9aa1ac;
    --border: #2a2e37;
    --verde: #1f8a4c;
    --verde-bg: #10301f;
    --amarelo: #b8860b;
    --amarelo-bg: #332a10;
  }}
  @media (prefers-color-scheme: light) {{
    :root {{
      --bg: #f5f6f8;
      --card: #ffffff;
      --text: #1a1d23;
      --muted: #5c6270;
      --border: #e2e4e9;
      --verde-bg: #e6f4ea;
      --amarelo-bg: #fbf1da;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px 16px 48px;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 4px; }}
  .subtitulo {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 20px; }}
  .resumo {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 20px;
  }}
  .cartao {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    flex: 1;
    min-width: 140px;
  }}
  .cartao .numero {{ font-size: 1.6rem; font-weight: 700; }}
  .cartao .rotulo {{ color: var(--muted); font-size: 0.8rem; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 10px; overflow: hidden; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
  th {{ color: var(--muted); font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em; }}
  tr:last-child td {{ border-bottom: none; }}
  a {{ color: inherit; text-decoration: underline; text-decoration-color: var(--muted); }}
  .badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    white-space: nowrap;
  }}
  .badge-viavel {{ background: var(--verde-bg); color: var(--verde); }}
  .badge-alto {{ background: var(--amarelo-bg); color: var(--amarelo); }}
  .badge-neutro {{ background: transparent; color: var(--muted); }}
  .cpm {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .data {{ color: var(--muted); white-space: nowrap; font-size: 0.8rem; }}
  .vazio {{ text-align: center; padding: 40px; color: var(--muted); }}
  .rodape {{ margin-top: 20px; color: var(--muted); font-size: 0.78rem; text-align: center; }}
  @media (max-width: 640px) {{
    table, thead, tbody, th, td, tr {{ display: block; }}
    thead {{ display: none; }}
    tr {{ border-bottom: 1px solid var(--border); padding: 12px; }}
    td {{ border-bottom: none; padding: 4px 0; }}
    td::before {{ content: attr(data-rotulo); display: block; color: var(--muted); font-size: 0.72rem; text-transform: uppercase; }}
  }}
</style>
</head>
<body>
  <div class="container">
    <h1>📊 Monitor de Milhas</h1>
    <p class="subtitulo">Atualizado em {atualizado_em} · teto de CPM: R$ {CPM_MAXIMO_ALERTA:.2f}</p>

    <div class="resumo">
      <div class="cartao"><div class="numero">{total}</div><div class="rotulo">promoções encontradas</div></div>
      <div class="cartao"><div class="numero">{viaveis}</div><div class="rotulo">viáveis agora</div></div>
    </div>

    {"" if promocoes else '<div class="vazio">Nenhuma promoção encontrada ainda.</div>'}
    {"" if not promocoes else f'''<table>
      <thead>
        <tr>
          <th>Status</th>
          <th>CPM</th>
          <th>Promoção</th>
          <th>De → Para</th>
          <th>Bônus Máx</th>
          <th>Descoberto em</th>
        </tr>
      </thead>
      <tbody>
        {linhas}
      </tbody>
    </table>'''}

    <p class="rodape">Gerado automaticamente pelo meu-monitor-milhas a cada execução.</p>
  </div>
</body>
</html>
"""


def gerar_dashboard():
    init_db()
    promocoes = listar_promocoes()
    conteudo = gerar_html(promocoes)
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print(f"Painel gerado em: {SAIDA} ({len(promocoes)} promoções)")


if __name__ == "__main__":
    gerar_dashboard()
