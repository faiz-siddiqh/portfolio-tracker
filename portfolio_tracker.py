import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from mutual_funds import calculate_mutual_fund_portfolio
from crypto import calculate_crypto_portfolio

# Cache for fetched stock data
stock_cache = {}

# Function to fetch multiple stock prices at once
def fetch_stock_prices(tickers, retries=3, delay=5):
    global stock_cache
    tickers = list(set(tickers))  # Remove duplicates

    # Check cache first
    missing_tickers = [t for t in tickers if t not in stock_cache]

    if not missing_tickers:
        return {t: stock_cache[t] for t in tickers}

    for attempt in range(retries):
        try:
            data = yf.download(missing_tickers, period="1mo")["Close"]

            if data.empty:
                raise ValueError("No historical data available")

            latest_prices = data.iloc[-1].to_dict()

            # Store in cache
            for ticker, price in latest_prices.items():
                stock_cache[ticker] = {"current_price": price, "error": None}

            return {t: stock_cache[t] for t in tickers}

        except Exception as e:
            if "Too Many Requests" in str(e) and attempt < retries - 1:
                st.warning(f"Rate limited. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                return {t: {"current_price": None, "error": str(e)} for t in tickers}

# Function to fetch INR to USD exchange rate
def get_inr_to_usd():
    try:
        data = yf.Ticker("USDINR=X").history(period="1d")
        if data.empty:
            raise ValueError("No exchange rate data available")

        inr_to_usd = data["Close"].iloc[-1]
        return 1 / inr_to_usd if inr_to_usd else None
    except Exception as e:
        st.error(f"Error fetching exchange rate: {str(e)}")
        return None

# Function to calculate portfolio stats
def calculate_portfolio(df, currency, conversion_rate):
    tickers = df["Ticker"].str.strip().str.upper().tolist()
    stock_data = fetch_stock_prices(tickers)

    total_value = 0
    valid_stocks = []

    for _, row in df.iterrows():
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

        market_value = current_price * shares * conversion_rate
        return_percent = ((current_price - avg_cost_basis) / avg_cost_basis) * 100
        total_value += market_value

        valid_stocks.append({
            "Ticker": ticker,
            "Shares": shares,
            "Avg. Cost Basis": avg_cost_basis,
            "Current Price (USD)": current_price * conversion_rate,
            "Market Value (USD)": market_value,
            "Return (%)": return_percent,
            "Currency": currency
        })

    return valid_stocks, total_value

# Function to plot portfolio allocation
def plot_portfolio(portfolio):
    if not portfolio:
        st.warning("No valid data to plot.")
        return

    df = pd.DataFrame(portfolio)

    st.subheader("Portfolio Holdings")
    col1, col2 = st.columns(2)

    half = len(df) // 2
    with col1:
        st.dataframe(df.iloc[:half].style.format({'Current Price (USD)': '${:.2f}', 'Market Value (USD)': '${:.2f}', 'Return (%)': '{:.2f}%'}))
    with col2:
        st.dataframe(df.iloc[half:].style.format({'Current Price (USD)': '${:.2f}', 'Market Value (USD)': '${:.2f}', 'Return (%)': '{:.2f}%'}))

    st.subheader("Portfolio Allocation")
    fig = px.pie(df, values='Market Value (USD)', names='Ticker', hole=0.2, labels={'Ticker': 'Ticker'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_traces(marker=dict(colors=px.colors.qualitative.Set2))

    fig.update_layout(
        hovermode="x unified",
        showlegend=True,
        legend_title="Stocks",
        margin=dict(t=50, l=25, r=25, b=25)
    )
    st.plotly_chart(fig, use_container_width=True)

# Main function
def main():
    st.title("Global Portfolio Tracker (USD)")

    inr_to_usd = get_inr_to_usd() or 1

    portfolio_files = [
        ("indian_portfolio.csv", "INR", inr_to_usd),
        ("us_portfolio.csv", "USD", 1)
    ]

    combined_portfolio = []
    total_usd_value = 0
    portfolio_values = {}

    for file_path, currency, rate in portfolio_files:
        full_path = os.path.join(os.getcwd(), file_path)

        try:
            df = pd.read_csv(full_path).dropna(subset=["Ticker"])

            if not all(col in df.columns for col in ["Ticker", "Shares", "Avg. Cost Basis"]):
                st.error(f"CSV file {file_path} is missing required columns.")
                continue

            portfolio, total_value = calculate_portfolio(df, currency, rate)
            combined_portfolio.extend(portfolio)
            total_usd_value += total_value
            portfolio_values[currency] = total_value

        except FileNotFoundError:
            st.error(f"Portfolio CSV file not found: {file_path}")
        except Exception as e:
            st.error(f"Error reading {file_path}: {str(e)}")

    # Mutual Fund Portfolio Calculation
    try:
        df_mutual = pd.read_csv("mutual_fund_portfolio.csv")
        mutual_fund_portfolio, mutual_fund_value = calculate_mutual_fund_portfolio(df_mutual, inr_to_usd)
        total_usd_value += mutual_fund_value
        portfolio_values["Mutual Funds"] = mutual_fund_value
    except FileNotFoundError:
        st.error("Mutual fund portfolio file not found.")

    # Cryptocurrency Portfolio Calculation
    try:
        df_crypto = pd.read_csv("crypto_portfolio.csv")
        crypto_portfolio, crypto_value = calculate_crypto_portfolio(df_crypto)
        total_usd_value += crypto_value
        portfolio_values["Cryptocurrency"] = crypto_value
    except FileNotFoundError:
        st.error("Crypto portfolio file not found.")

    # Display individual portfolio values
    for category, value in portfolio_values.items():
        st.success(f"Total {category} Portfolio Value in USD: ${value:,.2f}")

    # Display total portfolio value
    st.success(f"Total Portfolio Value: ${total_usd_value:,.2f}")

    # Plot only stocks (excluding mutual funds and crypto)
    plot_portfolio(combined_portfolio)

if __name__ == "__main__":
    main()