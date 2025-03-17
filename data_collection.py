import os
from dotenv import load_dotenv
from fredapi import Fred
import yfinance as yf
import pandas as pd
from datetime import timedelta

# Nastavíme konečné datum na dnešní datum + 1 den (protože 'end' je exkluzivní)
FIXED_END_DATE = "2025-03-14"
START_DATE = "2019-01-01"  # Pozor: tento start date můžeš upravit dle potřeby

def fix_timezone(df, date_col="Date"):
    """
    Pokud sloupec s datem obsahuje časovou zónu, odeber ji (bez DeprecationWarning).
    """
    if not df.empty and date_col in df.columns:
        if isinstance(df[date_col].dtype, pd.DatetimeTZDtype):
            df[date_col] = df[date_col].dt.tz_localize(None)
    return df

def fetch_btc_data(start_date=START_DATE, end_date=FIXED_END_DATE):
    btc = yf.download("BTC-USD", start=start_date, end=end_date, interval="1d", auto_adjust=False)
    if not btc.empty:
        btc = btc[["Close", "Volume"]].reset_index()
        btc.columns = ["Date", "BTC_Close", "BTC_Volume"]
        btc = fix_timezone(btc, "Date")
    return btc

def fetch_sp500_data(start_date=START_DATE, end_date=FIXED_END_DATE):
    sp500 = yf.download("^GSPC", start=start_date, end=end_date, interval="1d", auto_adjust=False)
    if not sp500.empty:
        sp500 = sp500[["Close"]].reset_index()
        sp500.columns = ["Date", "SP500_Close"]
        sp500 = fix_timezone(sp500, "Date")
    return sp500

def fetch_m2_data(start_date=START_DATE, end_date=FIXED_END_DATE):
    load_dotenv()  # načte FRED_API_KEY z .env
    FRED_API_KEY = os.getenv("FRED_API_KEY")
    fred = Fred(api_key=FRED_API_KEY)
    m2_series = fred.get_series("M2SL", observation_start=start_date, observation_end=end_date)
    m2_df = m2_series.to_frame(name="M2")
    m2_df.index.name = "Date"
    m2_df.index = pd.to_datetime(m2_df.index)
    # Resample na denní frekvenci a doplnění metodou ffill
    m2_df = m2_df.resample("D").ffill().reset_index()
    m2_df = fix_timezone(m2_df, "Date")
    return m2_df

if __name__ == "__main__":
    # Stáhneme data pro BTC, S&P500, M2
    btc_df = fetch_btc_data()
    sp500_df = fetch_sp500_data()
    m2_df = fetch_m2_data()

    if btc_df.empty:
        print("Upozornění: BTC data jsou prázdná, zkontroluj API nebo datum.")
    if sp500_df.empty:
        print("Upozornění: S&P500 data jsou prázdná, zkontroluj API nebo datum.")
    if m2_df.empty:
        print("Upozornění: M2 data jsou prázdná, zkontroluj API nebo klíč FRED.")

    merged = pd.merge(btc_df, sp500_df, on="Date", how="inner")
    merged = pd.merge(merged, m2_df, on="Date", how="inner")

    merged.to_csv("crypto_data.csv", index=False)
    print(f"Data uložena do crypto_data.csv (od {START_DATE} do {FIXED_END_DATE}).")
