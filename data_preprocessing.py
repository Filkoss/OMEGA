import pandas as pd

def create_regression_target(df, horizon=5):
    """
    Posune sloupec BTC_Close o 'horizon' dní dopředu
    a vytvoří 'Target_Close' (cena BTC za horizon dní).
    """
    df["Target_Close"] = df["BTC_Close"].shift(-horizon)
    df = df.dropna(subset=["Target_Close"])  # smaže posledních horizon řádků
    return df

if __name__ == "__main__":
    df = pd.read_csv("crypto_data.csv", parse_dates=["Date"])

    horizon_input = input("Zadej, kolik dní dopředu (horizon) chceš predikovat: ")
    horizon = int(horizon_input)

    df = create_regression_target(df, horizon=horizon)
    df.to_csv("crypto_data_prepared.csv", index=False)

    print(f"Data připravena pro regresi s horizon={horizon} dní (uloženo do crypto_data_prepared.csv).")
