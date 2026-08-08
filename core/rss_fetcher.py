import sys
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import mktime

import feedparser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RSS_FEEDS


@dataclass
class PostRSS:
    titulo: str
    link: str
    data_publicacao: datetime
    fonte: str


def _extrair_data(entry) -> datetime:
    if getattr(entry, "published_parsed", None):
        return datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
    if getattr(entry, "updated_parsed", None):
        return datetime.fromtimestamp(mktime(entry.updated_parsed), tz=timezone.utc)
    return datetime.now(timezone.utc)


def buscar_novos_posts(feeds: list[str] = None, horas: int = 24) -> list[PostRSS]:
    """Rastreia os feeds RSS e retorna posts publicados nas últimas `horas` horas."""
    feeds = feeds or RSS_FEEDS
    limite = datetime.now(timezone.utc) - timedelta(hours=horas)
    posts_recentes: list[PostRSS] = []

    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)
        fonte = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            data_publicacao = _extrair_data(entry)
            if data_publicacao >= limite:
                posts_recentes.append(
                    PostRSS(
                        titulo=entry.get("title", "Sem título"),
                        link=entry.get("link", ""),
                        data_publicacao=data_publicacao,
                        fonte=fonte,
                    )
                )

    return posts_recentes


if __name__ == "__main__":
    for post in buscar_novos_posts():
        print(f"[{post.fonte}] {post.titulo} -> {post.link}")
