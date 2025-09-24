import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
#from textblob import TextBlob
from transformers import pipeline

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
classifier = pipeline("sentiment-analysis", model=model_name)

class NewsSpider(scrapy.Spider):
    name = "news_spider"

    def __init__(self, url=None, item_list=None, *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.item_list = item_list  # Store the item list for collected data

    def parse(self, response):
        title = response.css('title::text').get()
        paragraphs = response.css('p::text').getall()

        # Extract and clean the paragraphs
        cleaned_paragraphs = CleanData.clean_paragraph(paragraphs)

        # Append scraped data to item list
        self.item_list.append({
            'title': title,
            'paragraphs': cleaned_paragraphs,
        })

class CleanData:
    @staticmethod
    def clean_paragraph(paragraphs):
        """Cleans the scraped paragraphs."""
        cleaned = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:  # Only add non-empty paragraphs
                cleaned.append(paragraph)
        return cleaned

scraped_data = []

def run_spider(url):
    """Runs the Scrapy spider and returns scraped data."""
    global scraped_data
    scraped_data = []  # Clear previous data
    process = CrawlerProcess(get_project_settings())
    process.crawl(NewsSpider, url=url, item_list=scraped_data)  # Pass the item list to collect data
    process.start()  # The script will block here until the crawling is finished
    return scraped_data  # Return the scraped data

def process_text(text):
    """Preprocess the text (e.g., lemmatization, cleaning)."""
    # Implement your text processing logic here
    return text  # Return the processed text

def get_sentiment(text):
    """Analyze sentiment of the text."""
    #sentiment_score = TextBlob(text).sentiment.polarity
    max_length = 512
    if len(text) > max_length:
        text = text[:max_length]
    sentiment_score = classifier(text)

    if sentiment_score[0]['label'] == 'NEGATIVE':
        score = -0.5
    elif sentiment_score[0]['label'] == 'POSITIVE':
        score = 0.5
    else:
        score = 0
    print(sentiment_score)
    return score
