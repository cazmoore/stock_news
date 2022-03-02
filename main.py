import config
import requests
from twilio.rest import Client

STOCK_NAME = "IBM"
COMPANY_NAME = "IBM"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# STEP 1: Use https://www.alphavantage.co/documentation/#daily
# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

# Get yesterday's closing stock price
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": config.STOCK_APIKEY,
    "outputsize": "compact"
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]

# Use list comprehension
data_list = [value for (key, value) in data.items()]
yesterday_closing_price = float(data_list[0]["4. close"])

# Get previous day's closing stock price
previous_closing_price = float(data_list[1]["4. close"])

# Get the absolute movement
difference = yesterday_closing_price - previous_closing_price

up_down = None
if difference > 0:
    up_down = "+"
elif difference < 0:
    up_down = "-"

# Get percentage movement
percentage = round((difference / yesterday_closing_price) * 100)

# Set news API parameters, assess size of movement and print news if over threshold
news_params = {
    "q": COMPANY_NAME,
    "searchIn": "title",
    "apiKey": config.NEWS_APIKEY,
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 10
}

if abs(percentage) > 0.5:
    # Get articles related to Company Name
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    news_data = news_response.json()["articles"]

    # Get first 3 articles
    news_data = news_data[:3]

    # Use twilio.com/docs/sms/quickstart/python to send a separate message with each article's title and
    # description to your phone number.

    # Create a new list of the first 3 article's headline and description using list comprehension.
    formatted_articles = [f"{STOCK_NAME}: {up_down}{percentage}%\nHeadline: {news['title']}. \nBrief: " 
                          f"{news['description']}\n Link: {news['url']}" for news in news_data]

    # Send articles via Twilio
    client = Client(config.account_sid, config.auth_token)

    for article in formatted_articles:
        message = client.messages.create(
            body=article,
            from_= config.from_number,
            to= config.to_number
        )

        print(message.status)
