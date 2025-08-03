from django.core.management.base import BaseCommand
from news.utils import fetch_news_from_rss
from news.models import Article, Category
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Scrapes news articles from multiple RSS feeds with fallback parsing and stores them.'

    def handle(self, *args, **kwargs):
        self.stdout.write("🔍 Starting multi-source news scraping...")

        NEWS_SOURCES = {
            'BBC News': "https://feeds.bbci.co.uk/news/rss.xml",
            'CNN': "http://rss.cnn.com/rss/cnn_topstories.rss",
            'NDTV': "https://feeds.feedburner.com/ndtvnews-top-stories",
            'Al Jazeera': "https://www.aljazeera.com/xml/rss/all.xml",
        }

        total_articles_added = 0
        general_category, _ = Category.objects.get_or_create(name='General')

        for source_name, feed_url in NEWS_SOURCES.items():
            self.stdout.write(f"🛁 Fetching from {source_name} ({feed_url})...")
            logger.info(f"Fetching from {source_name}...")

            articles_data = fetch_news_from_rss(feed_url, source_name)

            if not articles_data:
                self.stdout.write(self.style.WARNING(f"⚠️ No articles fetched from {source_name}."))
                logger.warning(f"No articles fetched from {source_name}.")
                continue

            added_count = 0
            for article_data in articles_data[:1]:  # Fetch 1 article per source (adjustable)
                try:
                    if Article.objects.filter(link=article_data['link']).exists():
                        logger.info(f"⏭️ Duplicate: {article_data['title']}")
                        continue

                    pub_date = article_data['publication_date'] or timezone.now()
                    if timezone.is_naive(pub_date):
                        pub_date = timezone.make_aware(pub_date)

                    Article.objects.create(
                        title=article_data['title'],
                        content=article_data['content'],
                        summary="",  # Generated on demand
                        link=article_data['link'],
                        source=article_data['source'],
                        author=article_data.get('source', 'Unknown'),
                        source_url=article_data['link'],
                        category=general_category,
                        published_date=pub_date,
                        approved=False
                    )

                    added_count += 1
                    logger.debug(f"✅ Saved: {article_data['title']}")

                except Exception as e:
                    logger.error(f"❌ Error saving article from {source_name}: {e} - {article_data.get('title', 'N/A')}")

            total_articles_added += added_count
            self.stdout.write(self.style.SUCCESS(f"✅ Added {added_count} new articles from {source_name}."))

        self.stdout.write(self.style.SUCCESS(f"🎉 Finished scraping. Total new articles: {total_articles_added}."))

        logger.info(f"Finished scraping. Total new articles: {total_articles_added}")
