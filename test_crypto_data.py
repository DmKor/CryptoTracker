from crypto_tracker_coingecko import get_crypto_data

price, change = get_crypto_data("BTC")

print(f"Цена Bitcoin: {price} USD")
print(f"Изменение за 24 часа: {change:+.2f}%")