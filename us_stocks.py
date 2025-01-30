import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Function to fetch stock data for US stocks
def fetch_stock_data(ticker):
    try:
        if not ticker:
            raise ValueError("Empty ticker symbol provided")

        stock = yf.Ticker(ticker)
        
        # Fetch historical data with validation
        data = None
        data_periods = ["1d", "1mo", "3mo"]
        for period in data_periods:
            data = stock.history(period=period)
            if not data.empty:
                break
        
        if data is None or data.empty:
            raise ValueError(f"No historical data available for {ticker}")
            
        # Get current price with explicit index handling
        current_price = data['Close'].iloc[-1]
        if pd.isnull(current_price):
            raise ValueError("Invalid closing price received")
            
        # Get fundamental data with validation
        info = stock.info
        pe_ratio = info.get('trailingPE', 'N/A')
        
        return {
            'current_price': current_price,
            'pe_ratio': pe_ratio,
            'error': None
        }
        
    except Exception as e:
        return {
            'current_price': None,
            'pe_ratio': None,
            'error': f"Error fetching {ticker}: {str(e)}"
        }


# Function to calculate portfolio stats
def calculate_portfolio(df):
    total_value = 0
    valid_stocks = []
    
    for index, row in df.iterrows():
        ticker = row['Ticker'].strip().upper()
        shares = float(row['Shares'])
        avg_cost_basis = float(row['Avg. Cost Basis'])
        
        # Validate input values first
        if not isinstance(shares, (int, float)) or shares <0:
            st.error(f"Invalid shares value for {ticker}: {shares}")
            continue
            
        if not isinstance(avg_cost_basis, (int, float)) or avg_cost_basis <0:
            st.error(f"Invalid cost basis for {ticker}: {avg_cost_basis}")
            continue
            
        # Fetch stock data
        stock_data = fetch_stock_data(ticker)
        
        if stock_data['error']:
            st.error(stock_data['error'])
            continue
            
        current_price = stock_data['current_price']
        pe_ratio = stock_data['pe_ratio']
        
        if current_price > 0:
            market_value = current_price * shares
            return_percent = ((current_price - avg_cost_basis) / avg_cost_basis) * 100
            total_value += market_value
            
            valid_stocks.append({
                "Ticker": ticker,
                "Shares": shares,
                "Avg. Cost Basis": avg_cost_basis,
                "Current Price": current_price,
                "Market Value": market_value,
                "Return (%)": return_percent,
                "P/E Ratio": pe_ratio
            })
            
    return valid_stocks, total_value

# Function to plot interactive portfolio allocation
def plot_portfolio(portfolio, title):
    if not portfolio:
        st.warning(f"No valid data to plot for {title}.")
        return
        
    df = pd.DataFrame(portfolio)
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Portfolio Holdings")
        st.dataframe(df.style.format({
            'Current Price': '${:.2f}',
            'Market Value': '${:.2f}',
            'Return (%)': '{:.2f}%'
        }))
        
    with col2:
        st.subheader(title)
        fig = px.pie(
            df,
            values='Market Value',
            names='Ticker',
            hole=0.3,
            labels={'Ticker': 'Ticker'},
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# Main Function
def main():
    st.title("US Portfolio Tracker")

    # Path to the local CSV file
    file_path = os.path.join(os.getcwd(), "us_portfolio.csv")

    try:
        df = pd.read_csv(file_path)
        
        # Validate CSV structure
        required_columns = ['Ticker', 'Shares', 'Avg. Cost Basis']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV missing required columns. Needed: {required_columns}")
            return
            
        # Clean data
        df = df.dropna(subset=['Ticker'])
        
    except FileNotFoundError:
        st.error(f"Portfolio CSV file not found at {file_path}")
        return
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        return

    # Display raw data with toggle
    if st.checkbox("Show raw portfolio data"):
        st.subheader("Raw US Portfolio Data")
        st.write(df)

    # Calculate portfolio stats
    portfolio, total_value = calculate_portfolio(df)

    # Display results
    if portfolio:
        st.success(f"Total Portfolio Value: ${total_value:,.2f}")
        plot_portfolio(portfolio, "Portfolio Allocation")
    else:
        st.error("No valid stocks could be processed in the portfolio")

if __name__ == "__main__":
    main()