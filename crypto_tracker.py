import requests

API_URL = "https://data-api.binance.vision/api/v3/ticker/24hr"


def get_crypto_data(symbol):
    response = requests.get(
        API_URL,
        params={"symbol": symbol},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    price = float(data["lastPrice"])
    change = float(data["priceChangePercent"])

    return price, change


symbol = "BTCUSDT"

price, change = get_crypto_data(symbol)

print(symbol, price, change)