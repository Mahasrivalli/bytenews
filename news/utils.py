import os
import string
import feedparser
from datetime import datetime
from time import mktime
from collections import Counter
from bs4 import BeautifulSoup
from newspaper import Article as NewsArticle, Config
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from gtts import gTTS
from django.conf import settings
from django.utils import timezone
import nltk

# ---------------------------
# 🔧 Ensure NLTK resources are available
# ---------------------------
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


# ---------------------------
# 🧼 Clean HTML tags
# ---------------------------
def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)


# ---------------------------
# 📰 Fetch news from RSS with fallback
# ---------------------------
def fetch_news_from_rss(feed_url, source_name):
    config = Config()
    config.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    config.request_timeout = 20

    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:3]:  # Limit to 5 during dev
        try:
            article_url = entry.link
            news = NewsArticle(article_url, config=config)

            try:
                news.download()
                news.parse()
                full_content = news.text.strip()

                if not full_content or len(full_content) < 200:
                    raise ValueError("Too short or empty content")

            except Exception as e:
                print(f"⚠️ Newspaper scrape failed: {e}")
                full_content = clean_html(entry.get('summary', '') or entry.get('description', ''))
                if not full_content or len(full_content) < 50:
                    continue  # still not enough content

            published_time = entry.get('published_parsed')
            published_date = datetime.fromtimestamp(mktime(published_time)) if published_time else timezone.now()

            if timezone.is_naive(published_date):
                published_date = timezone.make_aware(published_date)

            articles.append({
                'title': entry.title,
                'link': article_url,
                'source': source_name,
                'content': full_content,
                'publication_date': published_date
            })

        except Exception as e:
            print(f"⚠️ Error scraping article from {source_name}: {e}")
            continue

    return articles


# ---------------------------
# ✂️ Clean punctuation from text
# ---------------------------
def clean_text(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)


# ---------------------------
# 🧠 Generate extractive summary
# ---------------------------
def generate_summary(text, article_title="", num_sentences=3):
    if not text or not isinstance(text, str):
        return "No content available to summarize."

    sentences = sent_tokenize(text, language="english")
    if len(sentences) <= num_sentences:
        return text

    words = word_tokenize(clean_text(text).lower(), language="english")
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    word_frequencies = Counter(filtered_words)

    if article_title:
        title_words = word_tokenize(clean_text(article_title).lower(), language="english")
        for word in title_words:
            if word in word_frequencies:
                word_frequencies[word] += 0.5

    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(clean_text(sentence.lower()), language="english"):
            if word in word_frequencies:
                sentence_scores[i] = sentence_scores.get(i, 0) + word_frequencies[word]
        if i == 0:
            sentence_scores[i] += 1.0
        elif i == 1:
            sentence_scores[i] += 0.5

    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    summary = ' '.join([sentences[i] for i, _ in sorted(top_sentences)])
    return summary


# ---------------------------
# 🔊 Generate audio summary
# ---------------------------
def generate_audio_summary(summary_text, article_id):
    if not summary_text:
        return None

    try:
        tts = gTTS(text=summary_text[:5000], lang='en')
        audio_filename = f"{article_id}_summary.mp3"
        audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', audio_filename)
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        tts.save(audio_path)

        return f"{settings.MEDIA_URL}audio/{audio_filename}"
    except Exception as e:
        print(f"❌ Error generating audio: {e}")
        return None


# ---------------------------
# 🧪 Test block
# ---------------------------
if __name__ == "__main__":
    test_text = """
    Artificial Intelligence is transforming many industries.
    It helps automate tasks, generate insights, and improve efficiency.
    Companies worldwide are investing in AI research.
    Healthcare, education, and finance sectors benefit from AI applications.
    The future of AI looks bright with more innovations to come.
    """
    test_title = "Artificial Intelligence in Industry"
    print("🔍 Summary:")
    print(generate_summary(test_text, article_title=test_title, num_sentences=2))
