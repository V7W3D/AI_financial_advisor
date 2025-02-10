from yfinance import Ticker, Search
    
def get_quote_info(ticker, list_params : list[str]) -> dict:
    quote = Ticker(ticker).info
    result = {}
    for param in list_params:
        if not param in result.keys():
            result[param] = quote[param]
    return result

def get_news(ticker, max_results:int):
    search = Search(ticker, max_results)
    result = {}
    for article in search.news:
        if not article["title"] in result.keys():
            result[article["title"]] = article["link"]
    return result