import requests

def get_mkt(token_address):
    splited = token_address.split('::')
    used_address =splited[0]
    url = f"https://api.blockberry.one/sui/v1/coins/{used_address}%3A%3A{splited[-2]}%3A%3A{splited[-1]}"
    # url = "https://api.blockberry.one/sui/v1/coins/0x9e6d6124287360cc110044d1f1d7d04a0954eb317c76cf7927244bef0706b113%3A%3ASCUBA%3A%3ASCUBA"

    headers = {
        "accept": "*/*",
        "x-api-key": "6h9mOZJPKSnOLYbqs66pvu3zyYGXtp"
    }

    response = requests.get(url, headers=headers)

    print(response.json()['fdv'])

get_mkt('0x9e6d6124287360cc110044d1f1d7d04a0954eb317c76cf7927244bef0706b113::SCUBA::SCUBA')