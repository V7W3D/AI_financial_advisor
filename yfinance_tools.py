from yfinance import Ticker, Search

class yfinance_tools:
    ticker : str

    def __init__(self, ticker:str):
        self.ticker = ticker
    
    def get_quote_info(self, list_params : list[str]) -> dict:
        quote = Ticker(self.ticker).info
        result = {}
        for param in list_params:
            if not param in result.keys():
                result[param] = quote[param]
        return result
    
    def get_news(self, max_results:int):
        search = Search(self.ticker, max_results)
        result = {}
        for article in search.news:
            if not article["title"] in result.keys():
                result[article["title"]] = article["link"]
        return result