import yfinance as yf

def fetch_stock_data(ticker, start_date, end_date):
    """Télécharge les données historiques d'un ticker sur Yahoo Finance."""
    data = yf.download(ticker, start=start_date, end=end_date)
    data.reset_index(inplace=True)  # Convertir l'index en colonne
    return data

# Exemple : Données AAPL pour 2023
aapl_data_2023 = fetch_stock_data("AAPL", "2023-01-01", "2023-12-31")
aapl_data_2023.to_csv("../data/AAPL_yahoo_data_2023.csv", index=False)
print("Données sauvegardées dans AAPL_yahoo_data_2023.csv")