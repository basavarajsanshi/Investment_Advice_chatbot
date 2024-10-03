from google.cloud import dialogflow_v2 as dialogflow
import os
import requests
from stock_data import get_stock_price

# Alpha Vantage API key
API_KEY = 'HCDFIE8D7OB0V3N8'

# Set the path to your service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\basav\investment_chatbot\lyrical-carver-437510-m7-b60cc12d5440.json"

# Function to interact with Dialogflow
def detect_intent_texts(project_id, session_id, texts, language_code='en'):
    session_client = dialogflow.SessionsClient()

    session = session_client.session_path(project_id, session_id)
    print(f"Session path: {session}\n")

    for text in texts:
        text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        # Debug: Print the query result to see what's returned
        print(f"Query result: {response.query_result}")
        
        return response.query_result

# Function to get stock symbol based on company name using Alpha Vantage
def get_stock_symbol_from_name(company_name):
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()

    if 'bestMatches' in data and len(data['bestMatches']) > 0:
        return data['bestMatches'][0]['1. symbol']
    else:
        return None

def extract_stock_name(query_text):
    query_words = query_text.lower().split()
    stock_keywords = ['of', 'for']
    for keyword in stock_keywords:
        if keyword in query_words:
            stock_index = query_words.index(keyword) + 1
            if stock_index < len(query_words):
                return query_words[stock_index].capitalize()
    return None

# Use the stock_data function to get stock price
def fetch_stock_price(query_result):
    print(f"Intent parameters: {query_result.parameters}")  # Debug print
    print(f"Query text: {query_result.query_text}")  # Debug print
    
    if query_result.intent.display_name == 'GetStockPrice.':
        stock = query_result.parameters.get('stock')
        
        if not stock or len(stock.split()) > 1:  # If stock is empty or contains multiple words
            # If Dialogflow failed to extract the stock, try our custom extraction
            stock = extract_stock_name(query_result.query_text)
        
        if stock:
            stock = stock.strip()
            print(f"Extracted stock name: {stock}")  # Debug print
            
            stock_symbol = get_stock_symbol_from_name(stock)
            
            if stock_symbol:
                price = get_stock_price(stock_symbol)
                return f"The current stock price of {stock} ({stock_symbol}) is ${price}"
            else:
                return f"Sorry, I couldn't find the stock symbol for {stock}."
        else:
            return query_result.fulfillment_text or "I couldn't capture the stock name. Can you please provide a specific company name?"
    elif query_result.intent.display_name == 'Greeting':
        return query_result.fulfillment_text or "Hello! How can I help you with stocks today?"
    
    return None

if __name__ == "__main__":
    project_id = "lyrical-carver-437510-m7"
    session_id = "12345"  # You can generate or use a static session ID

    while True:
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Get the Dialogflow response
        query_result = detect_intent_texts(project_id, session_id, [user_input])

        # Fetch the stock price if the intent is GetStockPrice
        response = fetch_stock_price(query_result)
        
        if response:
            print(f"Bot: {response}")
        elif query_result.fulfillment_text:
            print(f"Bot: {query_result.fulfillment_text}")
        else:
            print("Bot: I'm not sure how to respond to that. Can you ask about a specific stock?")
