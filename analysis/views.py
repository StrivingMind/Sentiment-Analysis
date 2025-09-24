import json
import asyncio
from django.shortcuts import render
from concurrent.futures import ThreadPoolExecutor
from .spiders.news_spider import run_spider, CleanData, process_text, get_sentiment

# Create a thread pool executor for blocking tasks
executor = ThreadPoolExecutor()

async def index(request):
    title = ""
    url = ""
    sentiment = ""
    cleaned_texts = []

    if request.method == "POST":
        url = request.POST.get('url')

        # Run the Scrapy spider in a thread
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(executor, run_spider, url)

        if data:
            cleaner = CleanData()

            for entry in data:
                entry['paragraphs'] = cleaner.clean_paragraph(entry['paragraphs'])
                cleaned_text = " ".join(entry['paragraphs'])
                lemmatized_text = await loop.run_in_executor(executor, process_text, cleaned_text)
                entry['cleaned_text'] = lemmatized_text
                entry['sentiment'] = await loop.run_in_executor(executor, get_sentiment, lemmatized_text)
                cleaned_texts.append(entry)

            # Prepare sentiment results
            if cleaned_texts:
                sentiments = [article['sentiment'] for article in cleaned_texts]
                sentiment = "The above article has a neutral impact."  # Default value
                if sentiments[0] > 0:
                    sentiment = "The above article has a positive impact."
                elif sentiments[0] < 0:
                    sentiment = "The above article has a negative impact."

                title = cleaned_texts[0].get('title', "No title found.")

    return render(request, 'analysis/sentiment_analysis.html', {
        'url': url,
        'title': title,
        'sentiment': sentiment,
        'cleaned_texts': cleaned_texts,
    })
