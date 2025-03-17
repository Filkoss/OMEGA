import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import pickle

if __name__ == "__main__":
    df = pd.read_csv("crypto_data_prepared.csv", parse_dates=["Date"])

    features = ["BTC_Close", "BTC_Volume", "SP500_Close", "M2"]
    X = df[features]
    y = df["Target_Close"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"MAE (Mean Absolute Error): {mae}")
    print(f"R^2 score: {r2}")

    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Regresní model uložen do model.pkl.")
