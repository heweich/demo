from django.core.cache import cache

from . import models

def get_self_article(author, ischange = False):
    articles = cache.get("self_articles")
    print("从缓存中拿取数据...")
    if articles is None or ischange:
        print("缓存中没有数据，开始查询数据库...")
        articles = models.Article.objects.filter(author=author)
        print("数据库查询到数据，正在同步到缓存中...")
        cache.set("self_articles",articles)

    return articles


def get_all_articles(ischange=False):
    articles = cache.get("all_articles")
    print("从缓存中获取数据...")
    if articles is None or ischange:
        print("缓存中没有数据，开始查询数据库...")
        articles = models.Article.objects.all()
        print("数据库查询到数据，正在同步到缓存中...")
        cache.set("all_articles",articles)

    return articles
