import logging
from telegram import Chat, ChatMember, ChatMemberUpdated, Update,InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,ChatMemberHandler,CallbackQueryHandler,ConversationHandler,MessageHandler,filters
import requests
import json
from decimal import Decimal, getcontext
from datetime import datetime, timedelta, timezone
import asyncio
from concurrent.futures import ThreadPoolExecutor
import mysql.connector
import time
from mysql.connector import Error
import threading
import random

ADD,NAME,WALLET =range(3)
keys = ['MSY01pmq3xvyd9oD22L4z5gAhl5xTx','KDATcAjpRGIUPFZXzYMfZDYGP6xOHE']

proxies_list = [
    {"http": "http://nejpopbg:zdtwx7to1lgq@199.187.190.42:7145", "https": "http://nejpopbg:zdtwx7to1lgq@199.187.190.42:7145"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@103.4.248.119:6427", "https": "http://nejpopbg:zdtwx7to1lgq@103.4.248.119:6427"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@207.228.35.249:6924", "https": "http://nejpopbg:zdtwx7to1lgq@207.228.35.249:6924"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@198.145.102.125:5481", "https": "http://nejpopbg:zdtwx7to1lgq@198.145.102.125:5481"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@192.46.186.229:5578", "https": "http://nejpopbg:zdtwx7to1lgq@192.46.186.229:5578"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@63.246.151.5:5336", "https": "http://nejpopbg:zdtwx7to1lgq@63.246.151.5:5336"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@69.30.74.116:5826", "https": "http://nejpopbg:zdtwx7to1lgq@69.30.74.116:5826"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@207.228.8.72:5158", "https": "http://nejpopbg:zdtwx7to1lgq@207.228.8.72:5158"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@192.46.186.124:5473", "https": "http://nejpopbg:zdtwx7to1lgq@192.46.186.124:5473"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@63.246.151.165:5496", "https": "http://nejpopbg:zdtwx7to1lgq@63.246.151.165:5496"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@103.196.8.15:5415", "https": "http://nejpopbg:zdtwx7to1lgq@103.196.8.15:5415"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@69.30.76.103:6499", "https": "http://nejpopbg:zdtwx7to1lgq@69.30.76.103:6499"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@62.164.241.211:8444", "https": "http://nejpopbg:zdtwx7to1lgq@62.164.241.211:8444"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@45.117.52.230:6267", "https": "http://nejpopbg:zdtwx7to1lgq@45.117.52.230:6267"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@69.30.74.38:5748", "https": "http://nejpopbg:zdtwx7to1lgq@69.30.74.38:5748"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@192.53.64.186:5464", "https": "http://nejpopbg:zdtwx7to1lgq@192.53.64.186:5464"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@130.180.239.17:6656", "https": "http://nejpopbg:zdtwx7to1lgq@130.180.239.17:6656"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@103.196.8.52:5452", "https": "http://nejpopbg:zdtwx7to1lgq@103.196.8.52:5452"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@207.228.8.77:5163", "https": "http://nejpopbg:zdtwx7to1lgq@207.228.8.77:5163"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@207.228.35.202:6877", "https": "http://nejpopbg:zdtwx7to1lgq@207.228.35.202:6877"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@199.187.190.72:7175", "https": "http://nejpopbg:zdtwx7to1lgq@199.187.190.72:7175"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@69.30.77.184:6924", "https": "http://nejpopbg:zdtwx7to1lgq@69.30.77.184:6924"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@168.158.184.231:6242", "https": "http://nejpopbg:zdtwx7to1lgq@168.158.184.231:6242"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@130.180.255.8:9699", "https": "http://nejpopbg:zdtwx7to1lgq@130.180.255.8:9699"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@82.140.159.172:6172", "https": "http://nejpopbg:zdtwx7to1lgq@82.140.159.172:6172"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@45.196.42.35:5424", "https": "http://nejpopbg:zdtwx7to1lgq@45.196.42.35:5424"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@207.228.35.131:6806", "https": "http://nejpopbg:zdtwx7to1lgq@207.228.35.131:6806"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@103.73.34.136:5536", "https": "http://nejpopbg:zdtwx7to1lgq@103.73.34.136:5536"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@5.182.198.82:5658", "https": "http://nejpopbg:zdtwx7to1lgq@5.182.198.82:5658"},
    {"http": "http://nejpopbg:zdtwx7to1lgq@207.135.196.39:6954", "https": "http://nejpopbg:zdtwx7to1lgq@207.135.196.39:6954"},
]

## ============ database =======================================#

PASSWORD_ = 'sui_mysqlpassword'

# MySQL database configuration
db_config = {
    'user': 'root',
    'password': 'Str0ng!Passw0rd',
    'host': 'localhost',
    'database': 'suidrops_db',
}

# # # MySQL database configuration
# db_config = {
#     'user': 'root',
#     'password': PASSWORD_,
#     'host': 'localhost',
#     'database': 'suiscanner',
# }

# Function to create a connection to the MySQL database
def create_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to create the token_wallets table if it doesn't exist
def create_table():
    conn = create_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()  
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS token_wallets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id BIGINT NOT NULL,
                token_address VARCHAR(255) NOT NULL,
                wallet_name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE(user_id, token_address)
            )
        """)
        conn.commit()
        print("Table 'token_wallets' checked/created successfully.")
    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to save or update the token address and wallet name for each user

def fetch_user_wallets(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT token_address, wallet_name FROM token_wallets 
            WHERE user_id = %s
            """,
            (user_id,)
        )
        return cursor.fetchall()  # Returns a list of tuples (token_address, wallet_name)
    finally:
        cursor.close()


def is_token_address_exists(user_id, token_address):
    conn = mysql.connector.connect(**db_config)  # Replace with your database config
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*) FROM token_wallets 
            WHERE user_id = %s AND token_address = %s
            """,
            (user_id, token_address)
        )
        result = cursor.fetchone()
        return result[0] > 0  # Returns True if the token address exists, False otherwise
    finally:
        cursor.close()
        conn.close()

def save_token_wallet(user_id, token_address, wallet_name):
    conn = mysql.connector.connect(**db_config)  # Replace with your database config
    cursor = conn.cursor()

    try:
        # Attempt to insert the wallet info
        cursor.execute(
            """
            INSERT INTO token_wallets (user_id, token_address, wallet_name)
            VALUES (%s, %s, %s)
            """,
            (user_id, token_address, wallet_name)
        )
        conn.commit()
        print("Wallet information saved successfully.")
    except mysql.connector.IntegrityError:
        # Handle the case where the wallet already exists
        print("This wallet is already added for this user.")
        return False  # Indicate that the wallet wasn't added
    finally:
        cursor.close()
        conn.close()
    return True  # Indicate that the wallet was added successfully
# Function to update the wallet name for a user's token address
def update_wallet_name(user_id: int, token_address: str, new_wallet_name: str) -> bool:
    # Truncate the token address to 64 characters
    token_address = token_address[:64]
    conn = create_connection()
    
    if conn is None:
        logging.error("Failed to connect to the database.")
        return False

    cursor = None
    try:
        cursor = conn.cursor()

        # Check if the token address exists for the user
        cursor.execute("""
            SELECT wallet_name 
            FROM token_wallets 
            WHERE user_id = %s AND LEFT(token_address, 64) = %s
        """, (user_id, token_address))
        
        result = cursor.fetchone()

        if result:
            # Update wallet name for the user and token address
            cursor.execute("""
                UPDATE token_wallets 
                SET wallet_name = %s 
                WHERE user_id = %s AND LEFT(token_address, 64) = %s
            """, (new_wallet_name, user_id, token_address))
            conn.commit()
            logging.info(f"Wallet name updated to '{new_wallet_name}' for user {user_id} and token address {token_address}.")
            return True
        else:
            logging.warning(f"No entry found for user {user_id} with token address {token_address}.")
            return False
    except Exception as e:  # Use Exception to catch all types of errors
        logging.error(f"Error updating wallet name: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_wallet_name(user_id: int, token_address: str) -> str:
    # Truncate the token address to 64 characters
    token_address = token_address[:64]
    conn = create_connection()
    
    if conn is None:
        return None  # Or raise an exception based on your error handling strategy

    cursor = None
    try:
        cursor = conn.cursor()

        # Fetch the wallet name for the user and token address
        cursor.execute("""
            SELECT wallet_name 
            FROM token_wallets 
            WHERE user_id = %s AND LEFT(token_address, 64) = %s
        """, (user_id, token_address))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return the wallet name
        else:
            print(f"No entry found for user {user_id} with token address {token_address}.")
            return None
    except Exception as e:  # Use Exception to catch all types of errors
        print(f"Error fetching wallet name: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# Function to delete a user's token address entry
def delete_token_wallet(user_id: int, token_address: str):
    # Truncate the token address to 64 characters
    token_address = token_address[:64]
    conn = create_connection()
    
    if conn is None:
        return

    cursor = None
    try:
        cursor = conn.cursor()

        # Check if the token address exists for the user
        cursor.execute("""
            SELECT wallet_name 
            FROM token_wallets 
            WHERE user_id = %s AND LEFT(token_address, 64) = %s
        """, (user_id, token_address))
        result = cursor.fetchone()

        if result:
            # Delete the entry for the user and token address
            cursor.execute("""
                DELETE FROM token_wallets 
                WHERE user_id = %s AND LEFT(token_address, 64) = %s
            """, (user_id, token_address))
            conn.commit()
            print(f"Deleted token address {token_address} for user {user_id}.")
        else:
            print(f"No entry found for user {user_id} with token address {token_address}.")
    except Exception as e:  # Use Exception to catch all types of errors
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


## ================== utils =================================#

def special_format(number):
    number = float(number)
    if number >= 1_000_000_000:  # Billions
        formatted = f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:  # Millions
        formatted = f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:  # Thousands
        formatted = f"{number / 1_000:.1f}K"
    elif number >= 0.000000001:  # Handle very small numbers (up to 9 decimal places)
        formatted = f"{number:.9f}".rstrip('0').rstrip('.')
    elif number > 0:  # Handle very small numbers using scientific notation
        formatted = f"{number:.9e}"
    else:  # Handle zero or negative numbers if needed
        formatted = f"{number:.9f}".rstrip('0').rstrip('.')
    return formatted

def is_address(ownder_address):
    url = f"https://api.blockberry.one/sui/v1/accounts/{ownder_address}/activity?size=20&orderBy=DESC"
    # api_keky= random.choice(keys)
    headers = {
        "accept": "*/*",
        "x-api-key": 'XYxEyo08B6FZ6ulFvOznTnhoPZvD0O'

    }
    
    response = requests.get(url, headers=headers)
    with open('file.json','w')as file:
        json.dump(response.json(),file,indent=4)
    if len(response.json()['content']) == 0:
        return None
    else:
        return 'GOOD'
    

def get_mkt(token_address):
    splited = token_address.split('::')
    used_address =splited[0]
    url = f"https://api.blockberry.one/sui/v1/coins/{used_address}%3A%3A{splited[-2]}%3A%3A{splited[-1]}"
    # url = "https://api.blockberry.one/sui/v1/coins/0x9e6d6124287360cc110044d1f1d7d04a0954eb317c76cf7927244bef0706b113%3A%3ASCUBA%3A%3ASCUBA"
    # key_api = random.choice(keys)
    headers = {
        "accept": "*/*",
        "x-api-key": 'XYxEyo08B6FZ6ulFvOznTnhoPZvD0O'
    }

    response = requests.get(url, headers=headers)
    with open('file.json','w')as file:
        json.dump(response.json(),file,indent=4)

    return response.json()['fdv']


def get_log(owner_address):
    url = f"https://api.blockberry.one/sui/v1/accounts/{owner_address}/activity?size=20&orderBy=DESC"
    # api_key = random.choice(keys)
    headers = {
        "accept": "*/*",
        "x-api-key": 'XYxEyo08B6FZ6ulFvOznTnhoPZvD0O'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to format amounts
def format_amount(amount):
    # Truncate to two decimal places without rounding
    truncated_amount = int(amount * 100) / 100.0
    return f"{truncated_amount:+.2f}"

# Dictionary to store tasks for each user and their wallets
user_wallet_tasks = {}
db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

async def fetch_user_wallets_users():
    """Fetch all wallet addresses from the database."""
    conn = db_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, token_address,wallet_name FROM token_wallets")  # Adjust table name
    wallets = cursor.fetchall()
    cursor.close()
    conn.close()
    return wallets



async def action(user_id, address, chat_id, name,context):
    """Monitor a specific wallet address and send a message for each new transaction."""
    logged_signatures = set()
    try:
        while True:
            print('working')
            parsed_data = get_log(address)  # Replace with actual data fetching logic
            if "content" in parsed_data and parsed_data["content"]:
                first_item = parsed_data["content"][0]  # Handle missing txHash with 'N/A'
                activity_type = first_item.get("activityType")
                if activity_type=='Swap':   
                    details = first_item.get("details", {})
                    details_dto = details.get("detailsDto", {})
                    sender = details_dto.get("sender")  # Handle missing sender with 'N/A'
                    tx_hash = details_dto.get("txHash")  # Handle missing txHash with 'N/A'
                    print(tx_hash)
                    if tx_hash not in logged_signatures:    
                        logged_signatures.add(tx_hash)
                        coins = details_dto.get("coins", [])
                        amounts = [coin.get("amount") for coin in coins]
                        symbols = [coin.get("symbol") for coin in coins]
                        coin_type = [coin.get("coinType") for coin in coins]

                        try:
                            mkt1=special_format(get_mkt(coin_type[0]))
                        except Exception as e:
                            mkt1 ='N/A'
                        try:
                            mkt2=special_format(get_mkt(coin_type[1]))
                        except Exception as e:
                            mkt2 = 'N/A'
                        try:
                            thenew_signer = f"{sender[:7]}...{sender[-4:]}"
                        except Exception as e:
                            thenew_signer ='N/A'
                        sign = f"<a href='https://suiscan.xyz/mainnet/account/{sender}'>{thenew_signer}</a>"
                        txn = f"<a href='https://suiscan.xyz/mainnet/tx/{tx_hash}'>TXN</a>"
                        if len(amounts) == 2 and len(symbols) == 2:
                            print(message)
                            message = (
                                f"<b>🧮Wallet Name: </b> {name}\n\n"
                                f"<b>✅Activity: </b> {activity_type}\n\n"
                                f"💰<code>{format_amount(amounts[0])}</code> <b>{symbols[0]}</b> ({mkt1} Mcap) for <code>{format_amount(amounts[1])}</code> <b>{symbols[1]}</b> ({mkt2} Mcap)\n"
                                f"👤:{sign}\n"
                                f"💵{txn}"
                            )
                            # prev_response = tx_hash
                            if message:
                                asyncio.run_coroutine_threadsafe(
                                    context.bot.send_message(chat_id=chat_id, text=message,parse_mode='HTML',disable_web_page_preview=True),
                                    asyncio.get_event_loop()
                            )
                            else:
                                print("The data does not match the expected format.")
                        else:
                            print('Already logged')

                elif activity_type  == 'Receive':
                    details = first_item.get("details", {})
                    details_dto = details.get("detailsDto", {})
                    tx_hash = details_dto.get("txHash", 'N/A')  # Handle missing txHash with 'N/A'
                    print(tx_hash)
                    if tx_hash not in logged_signatures: 
                        logged_signatures.add(tx_hash)
                        coins = details_dto.get("coins", [])

                        #coins = details_dto.get("coins", [])
                        amounts = [coin.get("amount") for coin in coins][-1]
                        symbols = [coin.get("symbol") for coin in coins][-1]
                        try:
                            mkt=special_format(get_mkt(coin_type))
                        except Exception as e:
                            mkt ='N/A'
                        txn = f"<a href='https://suiscan.xyz/mainnet/tx/{tx_hash}'>TXN</a>"
                        try:
                            thenew_signer = f"{address[:7]}...{address[-4:]}"
                        except Exception as e:
                            thenew_signer ='N/A'

                        sign = f"<a href='https://suiscan.xyz/mainnet/account/{address}'>{thenew_signer}</a>"

                        message = (
                                f"<b>🧮Wallet Name: </b> {name}\n\n"
                                f"<b>✅Activity: </b> {activity_type}\n\n"
                                f"💰<code>{format_amount(amounts)}</code> <b>{symbols}</b> ({mkt} Mcap)\n"
                                f"👤:{sign}\n"
                                f"💵{txn}"
                            )
                        print(message)
                        if message:
                            asyncio.run_coroutine_threadsafe(
                                context.bot.send_message(chat_id=chat_id, text=message,parse_mode='HTML',disable_web_page_preview=True),
                                asyncio.get_event_loop()
                            )
                            # await context.bot.send_message(chat_id, 'message', parse_mode='HTML', disable_web_page_preview=True)
                        else:
                            print("The data does not match the expected format.")

                elif activity_type  == 'Send':
                    details = first_item.get("details", {})
                    details_dto = details.get("detailsDto", {})
                    coins = details_dto.get("coins", [])
                    amounts = [coin.get("amount") for coin in coins][-1]
                    symbols = [coin.get("symbol") for coin in coins][-1]
                    tx_hash = first_item.get("digest")
                    if tx_hash not in logged_signatures: 
                        logged_signatures.add(tx_hash)
                        coin_type = [coin.get("coinType") for coin in coins][-1]
                        # print(format_amount(amounts),symbols)
                        try:
                            mkt=special_format(get_mkt(coin_type))
                        except Exception as e:
                            mkt ='N/A'
                        txn = f"<a href='https://suiscan.xyz/mainnet/tx/{tx_hash}'>TXN</a>"
                        try:
                            thenew_signer = f"{address[:7]}...{address[-4:]}"
                        except Exception as e:
                            thenew_signer ='N/A'
                        sign = f"<a href='https://suiscan.xyz/mainnet/account/{address}'>{thenew_signer}</a>"

                        
                        message = (
                                f"<b>🧮Wallet Name: </b> {name}\n\n"
                                f"<b>✅Activity: </b> {activity_type}\n\n"
                                f"💰<code>{format_amount(amounts)}</code> <b>{symbols}</b> ({mkt} Mcap)\n"
                                f"👤:{sign}\n"
                                f"💵{txn}"
                            )
                        # print(message)
                        # prev_response = tx_hash
                        print(message)
                        if message:
                            # asyncio.run_coroutine_threadsafe(
                            #     context.bot.send_message(chat_id=chat_id, text=message,parse_mode='HTML',disable_web_page_preview=True),
                            #     asyncio.get_event_loop()
                            # )
                            await context.bot.send_message(chat_id, message, parse_mode='HTML', disable_web_page_preview=True)
                        else:
                            print("The data does not match the expected format.")
                else:
                    details = first_item.get("details", {})
                    details_dto = details.get("detailsDto", {})
                    coins = details_dto.get("coins", [])
                    amounts = [coin.get("amount") for coin in coins][-1]
                    symbols = [coin.get("symbol") for coin in coins][-1]
                    tx_hash = first_item.get("digest")
                    if tx_hash not in logged_signatures: 
                        logged_signatures.add(tx_hash)
                        coin_type = [coin.get("coinType") for coin in coins][-1]
                        # print(format_amount(amounts),symbols)
                        try:
                            mkt=special_format(get_mkt(coin_type))
                        except Exception as e:
                            mkt ='N/A'
                        txn = f"<a href='https://suiscan.xyz/mainnet/tx/{tx_hash}'>TXN</a>"
                        try:
                            thenew_signer = f"{address[:7]}...{address[-4:]}"
                        except Exception as e:
                            thenew_signer ='N/A'
                        sign = f"<a href='https://suiscan.xyz/mainnet/account/{address}'>{thenew_signer}</a>"
                        
                        message = (
                                f"<b>🧮Wallet Name: </b> {name}\n\n"
                                f"<b>✅Activity: </b> {activity_type}\n\n"
                                f"💰<code>{format_amount(amounts)}</code> <b>{symbols}</b> ({mkt} Mcap)\n"
                                f"👤:{sign}\n"
                                f"💵{txn}"
                            )
                        print('this',message)
                        if message:
                            asyncio.run_coroutine_threadsafe(
                                context.bot.send_message(chat_id=chat_id, text=message,parse_mode='HTML',disable_web_page_preview=True),
                                asyncio.get_event_loop()
                            )
                            # await context.bot.send_message(chat_id, message, parse_mode='HTML', disable_web_page_preview=True)
                        else:
                            print("The data does not match the expected format.")
                        # prev_response = tx_hash
                    
            else:
                print("No activity found.")

            await asyncio.sleep(5)  # Non-blocking sleep
    except KeyError:
        await context.bot.send_message(chat_id, '❌Invalid Wallet Address', parse_mode='HTML', disable_web_page_preview=True)
    except Exception as e:
        print(f'an error {e} occured')
async def monitor_all_wallets(app):
    """Monitor all wallets from the database and dynamically add or remove tracking for each user."""
    global user_wallet_tasks
    try:
        while True:
            wallets = await fetch_user_wallets_users()
            # Organize wallet data by user
            user_wallet_map = {}
            for wallet in wallets:
                user_id = wallet['user_id']
                address = wallet['token_address']
                name = wallet['wallet_name']
                if user_id not in user_wallet_map:
                    user_wallet_map[user_id] = []
                user_wallet_map[user_id].append({
                    'address': address,
                    'wallet_name': name
                })
            # Start monitoring new wallets for each user
            for user_id, wallet_data in user_wallet_map.items():
                if user_id not in user_wallet_tasks:
                    user_wallet_tasks[user_id] = {}

                for wallet in wallet_data:
                    address = wallet['address']
                    name = wallet['wallet_name']  
                    if address not in user_wallet_tasks[user_id]:
                        print(f"Starting monitoring for user {user_id} wallet {address}")
                        user_wallet_tasks[user_id][address] = asyncio.create_task(action(user_id, address, user_id,name, app))
            # Check for wallet removals
            for user_id in list(user_wallet_tasks):
                for address in list(user_wallet_tasks[user_id]):
                    if not any(wallet['address'] == address for wallet in user_wallet_map.get(user_id, [])):
                        print(f"Stopping monitoring for user {user_id} wallet {address}")
                        user_wallet_tasks[user_id][address].cancel()
                        del user_wallet_tasks[user_id][address]
                if not user_wallet_tasks[user_id]:
                    del user_wallet_tasks[user_id]
            await asyncio.sleep(5)  # Adjust based on your desired update frequency
    except Exception as e:
        print('here',e)

def run_monitoring_in_thread(app):
    """Run the monitoring process in a separate thread."""
    # Create a new event loop for this thread
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)

    # Run the asynchronous function in this new loop
    new_loop.run_until_complete(monitor_all_wallets(app))
def start_monitoring_thread(app):
    print('strated monitoring....')
    """Create a thread for monitoring and start it."""
    monitoring_thread = threading.Thread(target=run_monitoring_in_thread, args=(app,), daemon=True)
    monitoring_thread.start()

#======================= bot ================================#
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update:Update,context : ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    chat_type:str = update.message.chat.type
    if chat_type == 'private':
        message = (
    "🎉 <b>Welcome to Emoji Wallet Tracker Bot! </b> 🎉\n\n"
    "🔍 Track any wallet and  receive real-time activity to enhance your analytics on the Sui Blockchain.\n\n"
    "🤔 For questions, join our socials and let's see if you can keep up:\n\n"
    "<a href='https://t.me/Suiemoji'>📱 Telegram</a> | <a href='https://x.com/SuiEmoji'>🐦 X</a> | <a href='https://hop.ag/swap/SUI-EMOJI'>💰 Buy Emoji</a>\n\n"
    "ℹ️ Support Emoji, Buy Emoji! 🎈"
)
        keyboard = [
                [
                    InlineKeyboardButton(text="➕Add Wallet", callback_data="add_wallet"),
                    InlineKeyboardButton(text="✏️Edit Wallet", callback_data="edit_wallet")
                ]
            ]
            
            # Create an inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(chat_id=user_id, photo=open('image.png', 'rb'),caption=message,parse_mode='HTML',reply_markup=reply_markup)



async def menu(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chat_id =update.message.chat.id
    btn2= InlineKeyboardButton("✏️Edit wallet", callback_data='edit_wallet')
    btn9= InlineKeyboardButton("➕ Add More to Main", callback_data='add_wallet')
    row2= [btn2]
    row9= [btn9]
    reply_markup = InlineKeyboardMarkup([row2,row9])
    message = (
        f"✅ Emoji Wallet Tracker\n\n"
        f"⚙️Menu"
    )
    await context.bot.send_message(chat_id=chat_id,text=message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)


async def button_query(update:Update,context : ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    original_message_id = query.message.message_id
    await query.answer()

    if query.data.startswith("0x"):  # Assuming wallet addresses start with '0x'
        wallet_address = query.data
        message = (
            f"Main\n"
            f"{wallet_address}..\n"
        )
        keyboard = [
                [
                    InlineKeyboardButton(text="✏️Rename", callback_data="rename"),
                    InlineKeyboardButton(text="🗑️Delete", callback_data="delete")
                ]
            ]
            # Create an inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=message,
        reply_markup=reply_markup
    )
        context.user_data['selected_wallet'] = wallet_address

    elif query.data == 'add_wallet':
        context.user_data['state'] = ADD
        message = (
            f"✅ Enter Wallet Address[💧SUI]: "
        )
        keyboard = [
                [
                    InlineKeyboardButton(text="❌Cancel", callback_data="cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # await query.edit_message_text(text=message,reply_markup=reply_markup)
        await context.bot.send_message(chat_id=chat_id,text=message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)
    elif query.data =='rename':
        print('rename')
        await context.bot.send_message(chat_id=chat_id,text='Please enter the new wallet name:')
        print(context.user_data.get('selected_wallet'))
        context.user_data['state'] = WALLET


    elif query.data == 'delete': 
        print('delete')
        wallet_address =context.user_data.get('selected_wallet')
        print(wallet_address)
        name = fetch_wallet_name(chat_id,wallet_address)
        message = (
            f"Do you want to remove wallet {name}?\n"
            
        )
        keyboard = [
                [
                    InlineKeyboardButton(text="🗑️Delete", callback_data="sure_delete"),
                    InlineKeyboardButton(text="❌Cancel", callback_data="sure_cancel")
                ]
            ]
            # Create an inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id,text=message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)


    elif query.data == 'sure_delete':
        wallet_address =context.user_data.get('selected_wallet')
        name = fetch_wallet_name(chat_id,wallet_address)
        delete_token_wallet(chat_id,wallet_address)

        message =(
            f"{name} wallet has been successfully removed from your watchlist"
        )

        await context.bot.send_message(chat_id=chat_id,text=message)


    elif query.data == 'sure_cancel':
        await context.bot.delete_message(chat_id=chat_id,message_id=original_message_id)
        await context.bot.send_message(chat_id,'Operation Delete was Canceled')

    elif query.data == 'edit_wallet':
        print('here')
        wallets = fetch_user_wallets(chat_id)
        if not wallets:
            await context.bot.send_message(chat_id=update.message.chat_id, text="You have no saved wallets.")
            return
        keyboard = []
        message = (
            f"✅ Emoji Wallet Tracker\n\n"
            f"✏️Select a wallet:"
        )
        for wallet in wallets:
            wallet_address = wallet[0][:64]  # Truncate if necessary
            wallet_name = wallet[1][:64]      # Truncate if necessary
            # Create the button
            button = InlineKeyboardButton(text=f"✅{wallet_name}", callback_data=wallet_address)
            keyboard.append([button])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send the message with the inline keyboard
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )

    elif query.data == 'cancel':
        await context.bot.delete_message(chat_id=chat_id,message_id=original_message_id)

    elif query.data == 'skip':
        btn2= InlineKeyboardButton("✏️Edit wallet", callback_data='edit_wallet')
        btn9= InlineKeyboardButton("➕ Add More to Main", callback_data='add_wallet')
        row2= [btn2]
        row9= [btn9]
        reply_markup = InlineKeyboardMarkup([row2,row9])
        token_address = context.user_data.get('token_address')
        wallet_name = token_address[:6]  # Use first six characters as the wallet name
    # Save token address and wallet name to the database
        message = f'''Wallet {wallet_name} has been added to Main watchlist!
You can customize wallet in Wallet settings.'''
        save_token_wallet(chat_id, token_address, wallet_name)       
        await context.bot.send_message(chat_id = chat_id,text =message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)
        

async def handle_message(update:Update,context:ContextTypes):
    chat_id = update.message.chat_id
    message_text = update.message.text
    
    if 'state' in context.user_data:
        if context.user_data['state'] == ADD:
            context.user_data['token_address'] = message_text
            # print(is_address(context.user_data['token_address']))
            if is_address(context.user_data['token_address']) != None and not is_token_address_exists(chat_id,context.user_data['token_address']):
                message =(
                    f"Enter Your Wallet Name (or press Skip and do it later in Wallet Settings)"
                )
                keyboard = [
                [
                    InlineKeyboardButton(text="Skip", callback_data="skip")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await context.bot.send_message(chat_id = chat_id,text =message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)
                context.user_data['state'] = NAME
            elif is_token_address_exists(chat_id,context.user_data['token_address']):
                message = f'''❌Wallet "{context.user_data['token_address']} already Exists!"'''
                await context.bot.send_message(chat_id = chat_id,text =message,parse_mode='HTML',disable_web_page_preview=True)
            else:
                keyboard = [
                [
                    InlineKeyboardButton(text="❌Cancel", callback_data="cancel")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_message(chat_id = chat_id,text ='Please enter a valid address.',reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)
        elif context.user_data['state'] == NAME:
            wallet_name = message_text
            token_address = context.user_data.get('token_address')
            print(token_address)
            if token_address:
                try:
                    save_token_wallet(chat_id, token_address, wallet_name)
                    btn2= InlineKeyboardButton("✏️Edit wallet", callback_data='edit_wallet')
                    btn9= InlineKeyboardButton("➕ Add More to Main", callback_data='add_wallet')
                    row2= [btn2]
                    row9= [btn9]
                    reply_markup = InlineKeyboardMarkup([row2,row9])
                    await context.bot.send_message(chat_id=chat_id, text=f"✅ Your wallet information has been saved with the name '{wallet_name}'.",reply_markup=reply_markup)
                    context.user_data.clear()
                except IndexError:
                    await context.bot.send_message(
                chat_id=chat_id,
                text="❌ An error occurred while saving your wallet or Wallet already Exist. Please try again."
            )
                context.user_data.clear()  # Clear user data after saving
                

            else:
                await context.bot.send_message(chat_id=chat_id, text='Token address not found. Please restart the process.')

        elif context.user_data['state'] == WALLET:
            # Update the wallet name in the database
            print('over')
            wallet_address=context.user_data.get('selected_wallet')
            print(wallet_address)
            update_wallet_name(chat_id,wallet_address, message_text)  # Replace with your update logic

            await context.bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Wallet renamed to '{message_text}'."
            )

            # # Clear the stored wallet address to reset the state
            context.user_data.clear()
        else:
        # If there's no state, prompt the user to start the process
            await context.bot.send_message(
                chat_id=chat_id,
                text="Please use the correct command to start the process."
            )

async def wallets(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    saved_wallets = fetch_user_wallets(chat_id)

    keyboard = []
    message = (
        f"✅ Emoji Wallet Tracker\n\n"
        f"✏️Select a wallet:"
    )
    for wallet in saved_wallets:
        wallet_address = wallet[0][:64]  # Truncate if necessary
        wallet_name = wallet[1][:64]      # Truncate if necessary
        # Create the button
        button = InlineKeyboardButton(text=f"✅{wallet_name}", callback_data=wallet_address)
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the inline keyboard
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=reply_markup
    )

async def add(update:Update,context:ContextTypes):
    chat_id = update.message.chat.id
    context.user_data['state'] = ADD
    message = (
        f"✅ Enter Wallet Address[💧SUI]: "
    )
    keyboard = [
            [
                InlineKeyboardButton(text="❌Cancel", callback_data="cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # await query.edit_message_text(text=message,reply_markup=reply_markup)
    await context.bot.send_message(chat_id=chat_id,text=message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)
        
async def help(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    message = (
        "✅ Emoji Wallet Tracker Commands:\n\n"
        "/menu - Call the main menu\n"
        "/add - Add a new Wallet or Coin\n"
        "/wallets - Get a list of added Wallets\n"
        "/help - Help section\n\n"
    )

    await context.bot.send_message(chat_id,message,parse_mode='HTML')


TOKEN_KEY_ = '7820482974:AAGicaWsIgY-JJ_5wqTGDqowDMXLxThGbJU'
# TOKEN_KEY_ = '7580227168:AAE8jOiX1vhwFemiZ5K29ixATQ2fNZCGRuQ'

async def on_startup(app):
    """Callback to start the monitoring process after the bot has started."""
    print("Bot started. Starting wallet monitoring...")
    # Start monitoring in a separate thread
    start_monitoring_thread(app)

def main():
    app = ApplicationBuilder().token(TOKEN_KEY_).build()
    create_table()
    start_monitoring_thread(app)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("wallets", wallets))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("help", help))

    # Handle add_wallet and edit_wallet first
    app.add_handler(CallbackQueryHandler(button_query))
    

    
    # Finally, handle text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == '__main__':
    main()

