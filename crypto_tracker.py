import requests

API_URL = "https://data-api.binance.vision/api/v3/ticker/24hr"

SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT"
]

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

def get_all_crypto_data():
    cryptos = []

    for symbol in SYMBOLS:
        try:
           price, change = get_crypto_data(symbol)

           cryptos.append({
               "symbol": symbol,
               "price": price,
               "change": change
                })

        except (
            requests.exceptions.RequestException,
            KeyError,
            ValueError
        ) as error:
            print(f"Ошибка получения {symbol}: {error}")

    return cryptos

    response.raise_for_status()

    data = response.json()

    price = float(data["lastPrice"])
    change = float(data["priceChangePercent"])

    return price, change


symbol = "BTCUSDT"

try:
    # price, change = get_crypto_data(symbol)
    # print(symbol, price, change)

    cryptos = get_all_crypto_data()

    for crypto in cryptos:
        print(
            crypto["symbol"],
            crypto["price"],
            crypto["change"]
        )

except requests.exceptions.RequestException as error:
    print("Ошибка:", error)

except KeyError as error:
    print("Отсутствует нужный ключ:", error)

except ValueError as error:
    print("Не удалось преобразовать значение во float:", error)