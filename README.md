# Portfolio Tracker

![Global_portfolio_tracker](https://github.com/user-attachments/assets/7d39ff37-1f35-43da-a16d-8a358056540a)

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

1. Create a CSV file named `us_portfolio.csv` and `indian_portfolio.csv` in the project directory with the following columns or use the sample one provided:
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

![Us_Portfolio_snapshot](https://github.com/user-attachments/assets/6e3deb1a-60ee-4bab-b0e9-4e73b2c0c011)
![newplot (4)](https://github.com/user-attachments/assets/8972673c-8285-4151-8f98-92f617df7abe)


2. For Indian Stocks Overview 
```bash
streamlit run indian_stocks.py
```
![Indian_Portfolio_snapshot](https://github.com/user-attachments/assets/779c7705-9ecd-4e18-8e40-8105b31ee49b)
![newplot (3)](https://github.com/user-attachments/assets/d0d32341-5124-4921-aa75-5382a2d79a97)

3. For Overall Portfolio Overview 
```bash
streamlit run portfolio_tracker.py
```
![Global_portfolio_tracker](https://github.com/user-attachments/assets/79cec321-9e98-4663-b56e-337ae36693d5)

This will start a local server and open the application in your default web browser.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

