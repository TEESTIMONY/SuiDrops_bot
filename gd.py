# import requests

# def get_mkt(token_address):
#     splited = token_address.split('::')
#     used_address =splited[0]
#     url = f"https://api.blockberry.one/sui/v1/coins/{used_address}%3A%3A{splited[-2]}%3A%3A{splited[-1]}"
#     # url = "https://api.blockberry.one/sui/v1/coins/0x9e6d6124287360cc110044d1f1d7d04a0954eb317c76cf7927244bef0706b113%3A%3ASCUBA%3A%3ASCUBA"

#     headers = {
#         "accept": "*/*",
#         "x-api-key": "6h9mOZJPKSnOLYbqs66pvu3zyYGXtp"
#     }

#     response = requests.get(url, headers=headers)

#     print(response.json()['fdv'])

# get_mkt('0x9e6d6124287360cc110044d1f1d7d04a0954eb317c76cf7927244bef0706b113::SCUBA::SCUBA')

















####  collect crid 
### get operators
## answer
import math

def addition(n1,n2):
    return n1+n2
    
def subtract(n1,n2):
    return n1-n2
    
def multiply(n1,n2):
    return n1*n2
    
def divide(n1,n2):
    return n1/n2

def square_root(n1):
    return math.sqrt(n1)

symbols ={
    '+':addition,
    '-':subtract,
    'x':multiply,
    '/':divide,
    '&':square_root
}

number_1 = float(input('Enter a number: '))

for items in symbols:
    print(items)
operator = input('choose an operator: ')
if operator in symbols:
    if operator == '&':
        action = symbols[operator]
        result = action(number_1)
        print(result)
    else:
        number_2 = float(input('Enter another number: '))
        action = symbols[operator]
        result = action(n1 = number_1,n2 = number_2)   ## key_word argument 
        print(result)

else:
    print('Invalid operator')
