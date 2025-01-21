import requests

API_KEY = "cu6l6q1r01qh2ki5utegcu6l6q1r01qh2ki5utf0"

def fetch_stock_price_finnhub(ticker, start_date, end_date):
    """Télécharge les prix historiques d'un ticker depuis Finnhub.io."""
    url = f"https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": ticker,
        "resolution": "D",  # Données journalières
        "from": int(pd.Timestamp(start_date).timestamp()),  # Conversion en timestamp UNIX
        "to": int(pd.Timestamp(end_date).timestamp()),
        "token": API_KEY,
    }
    response = requests.get(url, params=params)
    data = response.json()

    print("here's the fetched data : ", data)
    
    if data["s"] != "ok":
        raise Exception("Erreur lors de la récupération des données")
    
    # Conversion en DataFrame
    return pd.DataFrame({
        "Date": pd.to_datetime(data["t"], unit="s"),
        "Open": data["o"],
        "High": data["h"],
        "Low": data["l"],
        "Close": data["c"],
        "Volume": data["v"],
    })

# Exemple : Données AAPL pour 2023
import pandas as pd
aapl_data_finnhub = fetch_stock_price_finnhub("AAPL", "2023-01-01", "2023-12-31")
aapl_data_finnhub.to_csv("AAPL_finnhub_data_2023.csv", index=False)
print("Données sauvegardées dans AAPL_finnhub_data_2023.csv")
