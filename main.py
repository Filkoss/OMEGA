import pandas as pd
import pickle
from datetime import timedelta
from data_collection import fix_timezone
import yfinance as yf

def fetch_one_day(symbol, day):
    """
    Stáhne data z yfinance pro 1 den, ALE s koncem = day + 1 den.
    Pak vyfiltruje přesně řádek pro 'day'.
    """
    d1 = pd.to_datetime(day)
    d2 = d1 + pd.Timedelta(days=1)

    df = yf.download(symbol, start=d1, end=d2, interval="1d", auto_adjust=False)
    if df.empty:
        return pd.DataFrame()  # nic se nestáhlo

    df.reset_index(inplace=True)
    df = fix_timezone(df, "Date")

    # Vyfiltrujeme řádky, které mají Date odpovídající danému dni
    day_str = d1.strftime('%Y-%m-%d')
    df["Date_str"] = df["Date"].dt.strftime('%Y-%m-%d')
    df = df[df["Date_str"] == day_str]
    df.drop(columns=["Date_str"], inplace=True, errors="ignore")
    return df

def fetch_btc_one_day(day):
    df = fetch_one_day("BTC-USD", day)
    if not df.empty:
        df = df[["Date", "Close", "Volume"]].copy()
        df.columns = ["Date", "BTC_Close", "BTC_Volume"]
    return df

def fetch_sp500_one_day(day):
    df = fetch_one_day("^GSPC", day)
    if not df.empty:
        df = df[["Date", "Close"]].copy()
        df.columns = ["Date", "SP500_Close"]
    return df

def fetch_m2_one_day(day):
    # Pro M2 čteme z crypto_data.csv, kde máme kompletní data
    all_data = pd.read_csv("crypto_data.csv", parse_dates=["Date"])
    sub = all_data[all_data["Date"] == pd.to_datetime(day)]
    if sub.empty:
        return pd.DataFrame()
    sub = sub[["Date", "M2"]].copy()
    return sub

def make_prediction(from_date, days_ahead):
    btc_df = fetch_btc_one_day(from_date)
    sp500_df = fetch_sp500_one_day(from_date)
    m2_df = fetch_m2_one_day(from_date)

    if btc_df.empty or sp500_df.empty or m2_df.empty:
        print(f"Nepodařilo se stáhnout data pro {from_date} (BTC, SP500 nebo M2). "
              f"Možná je to víkend/svátek nebo chybí data M2 z CSV.")
        return

    data = pd.merge(btc_df, sp500_df, on="Date", how="inner")
    data = pd.merge(data, m2_df, on="Date", how="inner")

    if data.empty:
        print(f"Sloučený DataFrame je prázdný. Datum={from_date}")
        return

    features = ["BTC_Close", "BTC_Volume", "SP500_Close", "M2"]
    X = data[features]

    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
    except FileNotFoundError:
        print("Chyba: model.pkl neexistuje. Nejprve spusť model_training.py.")
        return

    future_price = model.predict(X)[0]
    current_price = data["BTC_Close"].iloc[0]
    pct_change = (future_price - current_price) / current_price

    if pct_change > 0.03:
        signal = "BUY"
    elif pct_change < -0.03:
        signal = "SELL"
    else:
        signal = "HOLD"

    target_date = pd.to_datetime(from_date) + pd.Timedelta(days=days_ahead)

    print("\n----------------------------------------------")
    print(f"Datum analýzy: {from_date}")
    print(f"Natrénovaný horizont: {days_ahead} dní")
    print(f"Aktuální cena BTC: {current_price:.2f} USD")
    print(f"Predikovaná cena za {days_ahead} dní: {future_price:.2f} USD")
    print(f"Odhadovaná změna: {pct_change:.2%} => Doporučení: {signal}")
    print(f"(Teoretické budoucí datum: {target_date.strftime('%Y-%m-%d')})")
    print("----------------------------------------------\n")

if __name__ == "__main__":
    from_date = input("Zadej datum, od kterého chceš predikovat (YYYY-MM-DD): ")
    days_ahead = int(input("Zadej počet dní dopředu (shodné s horizon, na který je natrénovaný model): "))
    make_prediction(from_date, days_ahead)
