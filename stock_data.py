import yfinance as yf

def get_stock_price(ticker):
    # Fetch the stock data
    stock = yf.Ticker(ticker)
    
    # Get the current price
    stock_info = stock.info
    current_price = stock_info.get('currentPrice')
    
    # Return the price or a message if not available
    if current_price:
        return f"The current price of {ticker} is ${current_price}."
    else:
        return "Sorry, couldn't fetch the stock price at the moment."

# Example usage
if __name__ == "__main__":
    ticker_symbol = input("Enter the stock ticker symbol: ").upper()
    print(get_stock_price(ticker_symbol))
