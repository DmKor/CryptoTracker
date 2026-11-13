
import requests
from getpass import getpass

API_URL = "https://api.coingecko.com/api/v3/simple/supported_vs_currencies"

api_key = getpass("Введите Demo API Key: ")

headers = {
    "x-cg-demo-api-key": api_key
}

try:
    response = requests.get(
        API_URL,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    currencies = response.json()

    print("Соединение с CoinGecko успешно!")

    if "usdt" in currencies:
        print("USDT поддерживается как валюта котировки.")
    else:
        print("USDT отсутствует среди поддерживаемых валют.")

except requests.exceptions.RequestException as error:
    print("Ошибка запроса:", error)
