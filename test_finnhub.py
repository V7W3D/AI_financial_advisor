import requests
response = requests.get("https://finnhub.io/api/v1/quote", 
                        params={"symbol": "AAPL", "token": "cu6l6q1r01qh2ki5utegcu6l6q1r01qh2ki5utf0"})
print(response.json())
