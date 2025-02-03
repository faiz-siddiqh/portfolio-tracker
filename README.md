# Portfolio Tracker

## Description

This project is a comprehensive tool designed to track and visualize portfolios of US stocks , Indian Stocks and Overall Portfolio. It provides an interactive interface to analyze your stock holdings, calculate returns, and view portfolio allocations.

**Future Updates:**
- Integration of cryptocurrency portfolios

## Features

- Fetches real-time stock data using Yahoo Finance API
- Calculates portfolio value and individual stock returns
- Visualizes portfolio allocation with interactive charts
- Handles errors and data inconsistencies gracefully

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/portfolio-tracker.git
   cd portfolio-tracker
   ```

2. Install required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Dependencies

- yfinance
- streamlit
- pandas
- plotly

## Setup

1. Create a CSV file named `us_portfolio.csv` in the project directory with the following columns:
   - Ticker
   - Shares
   - Avg. Cost Basis

2. Add your stock holdings to the CSV file.

## Usage

Run the application using Streamlit:

1. For US Stocks Overview 
```bash
streamlit run us_stocks.py
```

2. For Indian Stocks Overview 
```bash
streamlit run indian_stocks.py
```

3. For Overall Portfolio Overview 
```bash
streamlit run portfolio_tracker.py
```

This will start a local server and open the application in your default web browser.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

