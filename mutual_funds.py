import requests
import pandas as pd
import streamlit as st

def fetch_mutual_fund_nav(scheme_codes):
    base_url = "https://api.mfapi.in/mf/"
    nav_data = {}
    
    for scheme_code in scheme_codes:
        try:
            response = requests.get(base_url + str(scheme_code))
            data = response.json()
            if "data" in data and data["data"]:
                nav = float(data["data"][0]["nav"])
                nav_data[scheme_code] = nav
            else:
                nav_data[scheme_code] = None
        except Exception as e:
            st.error(f"Error fetching NAV for scheme {scheme_code}: {str(e)}")
            nav_data[scheme_code] = None
    
    return nav_data

def calculate_mutual_fund_portfolio(df, inr_to_usd):
    scheme_codes = df["Scheme Code"].tolist()
    nav_data = fetch_mutual_fund_nav(scheme_codes)
    
    total_value = 0
    mutual_fund_portfolio = []
    
    for _, row in df.iterrows():
        scheme_code = row["Scheme Code"]
        units = float(row["Units"])
        nav = nav_data.get(scheme_code, None)
        
        if nav is None:
            st.error(f"No NAV found for Scheme Code {scheme_code}")
            continue
        
        market_value = nav * units * inr_to_usd
        total_value += market_value
        
        mutual_fund_portfolio.append({
            "Scheme Code": scheme_code,
            "Units": units,
            "NAV (INR)": nav,
            "Market Value (USD)": market_value
        })
    
    return mutual_fund_portfolio, total_value