import tweepy
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils.timezone import now

# Twitter API Authentication
def authenticate_twitter():
    auth = tweepy.OAuthHandler("YOUR_CONSUMER_KEY", "YOUR_CONSUMER_SECRET")
    auth.set_access_token("YOUR_ACCESS_TOKEN", "YOUR_ACCESS_SECRET")
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api

# Fetch live tweets
def fetch_tweets(api, query, count=10):
    tweets = api.search_tweets(q=query, count=count, tweet_mode='extended')
    return [(tweet.user.screen_name, tweet.full_text, tweet.created_at) for tweet in tweets]

# Fetch Instagram data (simplified for demonstration)
def fetch_instagram_posts(url):
    driver = webdriver.Chrome()  # Ensure you have the right WebDriver
    driver.get(url)
    time.sleep(5)  # Allow page to load
    page_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(page_source, 'html.parser')
    posts = soup.find_all('div', {'class': 'some-class'})  # Adjust selector as per site changes
    return [post.text for post in posts]

# Save data to a PDF
def save_to_pdf(data, filename="forensic_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    y_position = 750
    
    c.drawString(30, 780, f"Forensic Report - {now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for entry in data:
        c.drawString(30, y_position, f"{entry}")
        y_position -= 20
        if y_position < 50:
            c.showPage()
            y_position = 750
    
    c.save()

# Example usage
if __name__ == "__main__":
    twitter_api = authenticate_twitter()
    tweets_data = fetch_tweets(twitter_api, "#example", 5)
    insta_data = fetch_instagram_posts("https://www.instagram.com/example/")
    
    all_data = [f"Twitter: @{tw[0]} - {tw[1]} ({tw[2]})" for tw in tweets_data]
    all_data += [f"Instagram: {post}" for post in insta_data]
    
    save_to_pdf(all_data)
