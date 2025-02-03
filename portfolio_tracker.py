import yfinance as yf
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Function to fetch stock data
def fetch_stock_data(ticker):
    try:
        if not ticker:
            raise ValueError("Empty ticker symbol provided")

        stock = yf.Ticker(ticker)
        
        # Fetch historical data
        data = stock.history(period="1mo")
        if data.empty:
            raise ValueError(f"No historical data available for {ticker}")
        
        current_price = data['Close'].iloc[-1]
        if pd.isnull(current_price):
            raise ValueError("Invalid closing price received")
            
        # Get fundamental data
        info = stock.info
        pe_ratio = info.get('trailingPE', 'N/A')
        
        return {'current_price': current_price, 'pe_ratio': pe_ratio, 'error': None}
    
    except Exception as e:
        return {'current_price': None, 'pe_ratio': None, 'error': f"Error fetching {ticker}: {str(e)}"}

# Function to fetch INR to USD exchange rate
def get_inr_to_usd():
    try:
        inr_to_usd = yf.Ticker("USDINR=X").history(period="1d")['Close'].iloc[-1]
        return 1 / inr_to_usd if inr_to_usd else None
    except Exception as e:
        st.error(f"Error fetching exchange rate: {str(e)}")
        return None

# Function to calculate portfolio stats
def calculate_portfolio(df, currency, conversion_rate):
    total_value = 0
    valid_stocks = []
    
    for index, row in df.iterrows():
        ticker = row['Ticker'].strip().upper()
        shares = float(row['Shares'])
        avg_cost_basis = float(row['Avg. Cost Basis'])
        
        stock_data = fetch_stock_data(ticker)
        if stock_data['error']:
            st.error(stock_data['error'])
            continue
        
        current_price = stock_data['current_price']
        pe_ratio = stock_data['pe_ratio']
        
        if current_price > 0:
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
                "P/E Ratio": pe_ratio,
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

    # Update layout BEFORE displaying the chart
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
    
    # Fetch exchange rate
    inr_to_usd = get_inr_to_usd()
    if inr_to_usd is None:
        st.error("Failed to fetch INR to USD conversion rate.")
        return
    
    # Load Indian portfolio
    indian_file_path = os.path.join(os.getcwd(), "indian_portfolio.csv")
    us_file_path = os.path.join(os.getcwd(), "us_portfolio.csv")
    
    combined_portfolio = []
    total_usd_value = 0
    
    for file_path, currency, rate in [(indian_file_path, "INR", inr_to_usd), (us_file_path, "USD", 1)]:
        try:
            df = pd.read_csv(file_path)
            df = df.dropna(subset=['Ticker'])
            portfolio, total_value = calculate_portfolio(df, currency, rate)
            combined_portfolio.extend(portfolio)
            total_usd_value += total_value
        except FileNotFoundError:
            st.error(f"Portfolio CSV file not found: {file_path}")
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
    
    # Display results
    if combined_portfolio:
        st.success(f"Total Portfolio Value: ${total_usd_value:,.2f}")
        plot_portfolio(combined_portfolio)
    else:
        st.error("No valid stocks could be processed in the portfolio")

if __name__ == "__main__":
    main()
