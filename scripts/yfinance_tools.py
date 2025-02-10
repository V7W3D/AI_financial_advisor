from yfinance import Ticker, Search

def get_quote_info(input_string: str) -> str:
    # Split the input string
    parts = [part.strip() for part in input_string.split(',')]
    
    # Validate input
    if len(parts) < 2:
        return "Invalid input. Please provide ticker and at least one parameter."
    
    ticker = parts[0]
    quote = Ticker(ticker).info
    
    # Collect results
    results = []
    for param in parts[1:]:
        if param not in quote:
            results.append(f"{param}: Not found")
        else:
            results.append(f"{param}: {quote[param]}")
    
    # Join results into a multi-line summary
    return "\n".join(results)


def get_news(ticker, max_results:int):
    search = Search(ticker, max_results)
    unique_articles = {}
    news_text = ""
    
    for article in search.news:
        if article["title"] not in unique_articles:
            unique_articles[article["title"]] = article["link"]
            news_text += f"Title: {article['title']}\nLink: {article['link']}\n\n"
    
    return news_text