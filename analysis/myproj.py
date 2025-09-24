import json
from django.shortcuts import render
from .spiders.news_spider import run_spider, CleanData, process_text, get_sentiment

def index(request):
    title = ""
    url = ""
    sentiment = ""
    cleaned_texts = []

    if request.method == "POST":
        url = request.POST.get('url')
        
        # Log the received URL in the terminal
        print(f"Received URL: {url}")
        
        # Run the Scrapy spider
        data = run_spider(url)

        # Log the raw scraped data in the terminal
        print(f"Scraped data: {data}")

        if data:
            cleaner = CleanData()
            cleaned_texts = []  # List to store cleaned texts

            for entry in data:
                entry['paragraphs'] = cleaner.clean_paragraph(entry['paragraphs'])
                cleaned_text = " ".join(entry['paragraphs'])
                lemmatized_text = process_text(cleaned_text)
                entry['cleaned_text'] = lemmatized_text
                entry['sentiment'] = get_sentiment(lemmatized_text)
                cleaned_texts.append(entry)

                # Log cleaned text and sentiment in the terminal
                print(f"Cleaned Text: {lemmatized_text}")
                print(f"Sentiment: {entry['sentiment']}")

            # Save the cleaned data
            with open('cleaned_scraped_data.json', 'w') as f:
                json.dump(cleaned_texts, f, indent=4)

            print("Data cleaning and sentiment analysis done.")

            # Prepare sentiment results
            if cleaned_texts:
                sentiments = [article['sentiment'] for article in cleaned_texts]
                if sentiments[0] > 0:
                    sentiment = "The above article has a positive impact."
                elif sentiments[0] < 0:
                    sentiment = "The above article has a negative impact."
                else:
                    sentiment = "The above article has a neutral impact."

                # Log the final sentiment output
                print(f"Final Sentiment: {sentiment}")

            title = cleaned_texts[0]['title'] if cleaned_texts else "No title found."

    return render(request, 'analysis/sentiment_analysis.html', {
        'url': url,
        'title': title,
        'sentiment': sentiment,
        'cleaned_texts': cleaned_texts,
    })
