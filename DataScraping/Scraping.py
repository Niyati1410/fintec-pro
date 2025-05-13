from ntscraper import Nitter
import pandas as pd
import time
from random import choice

# List of reliable Nitter instances (fallback if one fails)
NITTER_INSTANCES = [
    "https://nitter.net",
    "https://nitter.privacyredirect.com",
    "https://nitter.unixfox.eu",
]

# Initialize scraper with retry logic
def get_scraper_instance():
    max_retries = 3
    for _ in range(max_retries):
        instance = choice(NITTER_INSTANCES)  # Randomly select an instance
        try:
            scraper = Nitter(log_level=1, instances=instance)  # Enable logging
            print(f"Using Nitter instance: {instance}")
            return scraper
        except Exception as e:
            print(f"Failed to initialize {instance}. Retrying... Error: {e}")
            time.sleep(5)
    raise Exception("All Nitter instances failed. Try again later.")

# Define stock market keywords with tickers (including $ for better results)
companies = {
    "Apple": "$AAPL",
    "Amazon": "$AMZN",
    "Google": "$GOOGL",
    "Microsoft": "$MSFT",
}

# Dictionary to store tweet data
data = {
    'company': [],
    'link': [],
    'text': [],
    'user': [],
    'likes': [],
    'retweets': [],
    'comments': [],
}

# Function to scrape tweets with retries
def scrape_tweets(scraper, query, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            tweets = scraper.get_tweets(query, mode='term', number=100)
            if not tweets['tweets']:
                print(f"Attempt {attempt + 1}: No tweets found for {query}")
                time.sleep(delay)
                continue
            return tweets['tweets']
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {query}: {e}")
            time.sleep(delay)
    return []  # Return empty list if all retries fail

# Main scraping loop
scraper = get_scraper_instance()

for company, ticker in companies.items():
    print(f"\nScraping tweets for {company} ({ticker})...")
    tweets = scrape_tweets(scraper, ticker)
    
    if not tweets:
        print(f"No tweets found for {ticker}. Skipping...")
        continue
    
    for tweet in tweets:
        data['company'].append(company)
        data['link'].append(tweet.get('link', 'N/A'))
        data['text'].append(tweet.get('text', 'No Text'))
        data['user'].append(tweet.get('user', {}).get('name', 'Unknown'))
        data['likes'].append(tweet.get('stats', {}).get('likes', 0))
        data['retweets'].append(tweet.get('stats', {}).get('retweets', 0))
        data['comments'].append(tweet.get('stats', {}).get('comments', 0))
    
    print(f"Successfully scraped {len(tweets)} tweets for {ticker}")

# Save to CSV if data exists
if data['company']:
    df = pd.DataFrame(data)
    csv_filename = 'stock_tweets.csv'
    df.to_csv(csv_filename, index=False)
    print(f"\n✅ Successfully saved {len(df)} tweets to {csv_filename}")
else:
    print("\n❌ No tweets were scraped. Check your search terms or Nitter instances.")