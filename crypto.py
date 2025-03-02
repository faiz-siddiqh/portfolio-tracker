import yfinance as yf
import streamlit as st
import pandas as pd

def fetch_crypto_prices(tickers):
    crypto_data = {}
    
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if data.empty:
                raise ValueError(f"No data found for {ticker}")
            
            current_price = data['Close'].iloc[-1]
            crypto_data[ticker] = {"current_price": current_price, "error": None}
        except Exception as e:
            crypto_data[ticker] = {"current_price": None, "error": str(e)}
    
    return crypto_data

def calculate_crypto_portfolio(df):
    tickers = df["Ticker"].str.strip().str.upper().tolist()
    crypto_prices = fetch_crypto_prices(tickers)
    
    total_value = 0
    crypto_portfolio = []
    
    for _, row in df.iterrows():
        ticker = row["Ticker"].strip().upper()
        units = float(row["Units"])
        
        crypto_info = crypto_prices.get(ticker, {})
        current_price = crypto_info.get("current_price")
        error = crypto_info.get("error")
        
        if error:
            st.error(f"Error fetching {ticker}: {error}")
            continue
        
        market_value = current_price * units
        total_value += market_value
        
        crypto_portfolio.append({
            "Ticker": ticker,
            "Units": units,
            "Current Price (USD)": current_price,
            "Market Value (USD)": market_value,
        })
    
    return crypto_portfolio, total_value
