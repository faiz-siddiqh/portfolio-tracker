# Portfolio Tracker

## Description

This project is a comprehensive tool designed to track and visualize portfolios of US stocks. It provides an interactive interface to analyze your stock holdings, calculate returns, and view portfolio allocations.

**Future Updates:**
- Support for tracking Indian stocks
- Integration of cryptocurrency portfolios

## Features

- Fetches real-time stock data using Yahoo Finance API
- Calculates portfolio value and individual stock returns
- Visualizes portfolio allocation with interactive charts
- Handles errors and data inconsistencies gracefully

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/us-portfolio-tracker.git
   cd us-portfolio-tracker
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

```bash
streamlit run us_stocks.py
```

This will start a local server and open the application in your default web browser.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

