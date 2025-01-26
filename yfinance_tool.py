import yfinance as yf

def get_quote_info(ticker : str, list_params : list[str]) -> dict:
    quote = yf.Ticker(ticker).info
    result = {}
    for param in list_params:
        if not param in result.keys():
            result[param] = quote[param]
    return result

print(get_quote_info("AAPL", ["earningsGrowth", "totalRevenue"]))