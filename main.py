import requests
import json
import time

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

    return response.json()['fdv']

def get_log(ownder_address):
    url = f"https://api.blockberry.one/sui/v1/accounts/{ownder_address}/activity?size=20&orderBy=DESC"

    headers = {
        "accept": "*/*",
        "x-api-key": "6h9mOZJPKSnOLYbqs66pvu3zyYGXtp"
    }

    response = requests.get(url, headers=headers)

    with open('file.json','w')as file:
        json.dump(response.json(),file,indent=4)

    return response.json()

address ='0x90a8bd47a5113ec141e37f499693d91596c518f295d9e4ae7c457cb966133b2d'

parsed_data = get_log(address)
def format_amount(amount):
    return f"{amount:+.6f}"
# Extract relevant information
first_item =  parsed_data.get("content", [])[0]
activity_type = first_item.get("activityType")
if activity_type !='Receive' and activity_type !='Send':
    details = first_item.get("details", {})
    details_dto = details.get("detailsDto", {})
    sender = details_dto.get("sender")
    tx_hash = details_dto.get("txHash")
    coins = details_dto.get("coins", [])
    amounts = [coin.get("amount") for coin in coins]
    symbols = [coin.get("symbol") for coin in coins]
    coin_type = [coin.get("coinType") for coin in coins]
    mkt1=get_mkt(coin_type[0])
    mkt2=get_mkt(coin_type[1])
    if len(amounts) == 2 and len(symbols) == 2:
        print(f"{format_amount(amounts[0])} {symbols[0]} for {format_amount(amounts[1])} {symbols[1]}")
    else:
        print("The data does not match the expected format.")
    # Output the extracted data
    print(f"Activity Type: {activity_type}")
    print(f"Sender: {sender}")
    print(f"Transaction Hash: {tx_hash}")
    print(mkt1)
    print(mkt2)
elif activity_type  == 'Receive':
    details = first_item.get("details", {})
    details_dto = details.get("detailsDto", {})
    coins = details_dto.get("coins", [])
    amounts = [coin.get("amount") for coin in coins][-1]
    symbols = [coin.get("symbol") for coin in coins][-1]
    tx_hash = first_item.get("digest")
    coin_type = [coin.get("coinType") for coin in coins][-1]
    mkt=get_mkt(coin_type)
    print(amounts)
    print(symbols)
    print(tx_hash)
    print(mkt)
elif activity_type  == 'Send':
    details = first_item.get("details", {})
    details_dto = details.get("detailsDto", {})
    coins = details_dto.get("coins", [])
    amounts = [coin.get("amount") for coin in coins]
    symbols = [coin.get("symbol") for coin in coins]
    print(amounts)
    print(symbols)












# def get_log(owner_address):
#     url = f"https://api.blockberry.one/sui/v1/accounts/{owner_address}/activity?size=20&orderBy=DESC"

#     headers = {
#         "accept": "*/*",
#         "x-api-key": "6h9mOZJPKSnOLYbqs66pvu3zyYGXtp"
#     }

#     response = requests.get(url, headers=headers)

#     with open('file.json', 'w') as file:
#         json.dump(response.json(), file, indent=4)

#     return response.json()

# def format_amount(amount):
#     return f"{amount:+.6f}"  # Shows + for positive numbers and - for negative numbers

# # Address to monitor
# address = '0x0eed4f927816613e40cefb3dbbac8f7151db7c7ce5d44ed534a340c52bbfe836'

# def Action(address):
#     prev_response = None
# # Continuous monitoring
#     while True:
#         parsed_data = get_log(address)

#         # Extract relevant information
#         if "content" in parsed_data and parsed_data["content"]:
#             first_item = parsed_data["content"][0]
#             activity_type = first_item.get("activityType")
#             details = first_item.get("details", {})
#             details_dto = details.get("detailsDto", {})

#             sender = details_dto.get("sender")
#             tx_hash = details_dto.get("txHash")

#             coins = details_dto.get("coins", [])
#             amounts = [coin.get("amount") for coin in coins]
#             symbols = [coin.get("symbol") for coin in coins]

#             # Create a message for the bot
#             if prev_response !=tx_hash:
#                 if len(amounts) == 2 and len(symbols) == 2:
#                     message = (
#                         f"{format_amount(amounts[0])} {symbols[0]} for {format_amount(amounts[1])} {symbols[1]}\n"
#                         f"Activity Type: {activity_type}\n"
#                         f"Sender: {sender}\n"
#                         f"Transaction Hash: {tx_hash}"
#                     )
#                 else:
#                     message = "The data does not match the expected format."
#                 # Send the message to the Telegram bot
#                 print(message)
#                 prev_response =tx_hash
#             else:
#                 print('already logged')
#         else:
#             print("No activity found.")
#         # Wait for 5 seconds before the next iteration
#         time.sleep(5)
# Action(address)