# scan.py
import requests

def get_all_futures_pairs():
    url = "https://contract.mexc.com/api/v1/contract/detail"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()['data']
        return [item['symbol'] for item in data]
    else:
        raise Exception(f"MEXC API error: {response.status_code}, {response.text}")

# Test etmek için:
if __name__ == "__main__":
    print(get_all_futures_pairs())
