import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time

# Cache to store stock data and prevent redundant requests
cache = {}

# Function to fetch multiple stock data at once
def fetch_multiple_stocks(tickers, retries=3, delay=5):
    global cache
    tickers = list(set(tickers))  # Remove duplicates

    # Check cache for previously fetched data
    missing_tickers = [t for t in tickers if t not in cache]

    if not missing_tickers:
        return {t: cache[t] for t in tickers}

    for attempt in range(retries):
        try:
            data = yf.download(missing_tickers, period="1mo")['Close']
            
            if data.empty:
                raise ValueError("No historical data available")

            latest_prices = data.iloc[-1].to_dict()

            # Store fetched data in cache
            for ticker, price in latest_prices.items():
                cache[ticker] = {"current_price": price, "error": None}

            return {t: cache[t] for t in tickers}

        except Exception as e:
            if "Too Many Requests" in str(e) and attempt < retries - 1:
                st.warning(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                return {t: {"current_price": None, "error": str(e)} for t in tickers}

# Function to calculate portfolio stats
def calculate_portfolio(df):
    tickers = df["Ticker"].str.strip().str.upper().tolist()
    stock_data = fetch_multiple_stocks(tickers)

    total_value = 0
    valid_stocks = []

    for index, row in df.iterrows():
        ticker = row["Ticker"].strip().upper()
        shares = float(row["Shares"])
        avg_cost_basis = float(row["Avg. Cost Basis"])

        if shares <= 0 or avg_cost_basis <= 0:
            st.error(f"Invalid data for {ticker}: Shares {shares}, Cost {avg_cost_basis}")
            continue

        stock_info = stock_data.get(ticker, {})
        current_price = stock_info.get("current_price")
        error = stock_info.get("error")

        if error:
            st.error(f"Error fetching {ticker}: {error}")
            continue

        market_value = current_price * shares
        return_percent = ((current_price - avg_cost_basis) / avg_cost_basis) * 100
        total_value += market_value

        valid_stocks.append({
            "Ticker": ticker,
            "Shares": shares,
            "Avg. Cost Basis": avg_cost_basis,
            "Current Price": current_price,
            "Market Value": market_value,
            "Return (%)": return_percent
        })

    return valid_stocks, total_value

# Function to plot portfolio allocation
def plot_portfolio(portfolio):
    if not portfolio:
        st.warning("No valid data to plot.")
        return
    
    df = pd.DataFrame(portfolio)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Portfolio Holdings")
        st.dataframe(df.style.format({
            "Current Price": "${:.2f}",
            "Market Value": "${:.2f}",
            "Return (%)": "{:.2f}%"
        }))

    with col2:
        st.subheader("Portfolio Allocation")
        fig = px.pie(df, values="Market Value", names="Ticker", hole=0.3)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

# Main Function
def main():
    st.title("US Portfolio Tracker")

    file_path = os.path.join(os.getcwd(), "us_portfolio.csv")

    try:
        df = pd.read_csv(file_path)

        required_columns = ["Ticker", "Shares", "Avg. Cost Basis"]
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV missing required columns: {required_columns}")
            return

        df = df.dropna(subset=["Ticker"])

    except FileNotFoundError:
        st.error(f"Portfolio CSV file not found at {file_path}")
        return
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        return

    if st.checkbox("Show raw portfolio data"):
        st.subheader("Raw Portfolio Data")
        st.write(df)

    portfolio, total_value = calculate_portfolio(df)

    if portfolio:
        st.success(f"Total Portfolio Value: ${total_value:,.2f}")
        plot_portfolio(portfolio)
    else:
        st.error("No valid stocks processed.")

if __name__ == "__main__":
    main()
