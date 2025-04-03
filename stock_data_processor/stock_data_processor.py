import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_stock_data(symbol, api_key):
    """Fetch stock data from Alpha Vantage API"""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={"3TCWPX9NPQVDUS90"}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Failed to fetch data. Status code: {response.status_code}")
        return None
        
    data = response.json()
    
    # Check if there's an error message in the response
    if "Error Message" in data:
        print(f"API Error: {data['Error Message']}")
        return None
        
    return data

def process_stock_data(data):
    """Clean and process the stock data"""
    # Extract time series data
    time_series = data.get("Time Series (Daily)")
    if not time_series:
        print("No time series data found in the response")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(time_series, orient='index')
    
    # Rename columns
    df.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    }, inplace=True)
    
    # Convert to numeric values
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col])
    
    # Convert index to datetime and reset index
    df.index = pd.to_datetime(df.index)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'date'}, inplace=True)
    
    # Calculate fluctuation (high - low)
    df['fluctuation'] = df['high'] - df['low']
    
    return df

def analyze_fluctuation(df, top_n=5):
    """Find days with highest price fluctuations"""
    # Sort by fluctuation in descending order
    sorted_df = df.sort_values(by='fluctuation', ascending=False).head(top_n)
    return sorted_df

def main():
    print("Stock Price Data Processing")
    print("==========================")
    
    # Get user inputs
    symbol = input("Enter stock symbol (e.g., AAPL): ")
    api_key = input("Enter your Alpha Vantage API key: ")
    
    # Fetch data
    print(f"Fetching data for {symbol}...")
    data = fetch_stock_data(symbol, api_key)
    
    if not data:
        print("Failed to retrieve data. Exiting.")
        return
    
    # Process data
    df = process_stock_data(data)
    
    if df is not None:
        print("\nData preview:")
        print(df[['date', 'open', 'close', 'high', 'low']].head())
        
        # Find and display days with highest fluctuation
        print("\nTop 5 days with highest price fluctuation:")
        top_fluctuations = analyze_fluctuation(df)
        print(top_fluctuations[['date', 'open', 'high', 'low', 'close', 'fluctuation']])
        
        # Optional: Create a visualization
        plt.figure(figsize=(12, 6))
        plt.bar(top_fluctuations['date'].dt.strftime('%Y-%m-%d'), 
                top_fluctuations['fluctuation'],
                color='red')
        plt.title(f'Top 5 Days with Highest Price Fluctuation for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Fluctuation (High - Low)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()
