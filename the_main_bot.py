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
import traceback
import re
from apscheduler.jobstores.base import ConflictingIdError
ADD,NAME,WALLET =range(3)


PASSWORD_= 'Testimonyalade@2003'
db_config = {
    'user': 'root',
    'password': PASSWORD_,
    'host': 'localhost',
    'database': 'suiscanner',
}
# ========================== db ================================== #
def delete_wallet_from_db(wallet_address: str, user_id: int) -> bool:
    """Delete the wallet from the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Adjust the column name based on your database schema
        cursor.execute("""
            DELETE FROM wallets WHERE wallet_address = %s AND user_id = %s
        """, (wallet_address, user_id))
        
        conn.commit()

        # Check if any rows were affected
        if cursor.rowcount > 0:
            return True  # Wallet deleted successfully
        else:
            return False  # No wallet found to delete

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

    finally:
        cursor.close()
        conn.close()

def fetch_user_id_by_chat_id(chat_id: int) -> int:
    """Fetch user_id based on chat_id."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Query to fetch user_id from users table based on chat_id
        cursor.execute("SELECT user_id FROM users WHERE chat_id = %s", (chat_id,))
        result = cursor.fetchone()
        
        if result:
            return result[0]  # Return user_id
        else:
            return None  # User not found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        cursor.close()
        conn.close()


def rename_wallet_in_db(wallet_address, new_wallet_name):
    """Rename a wallet in the database given its address and new name."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Update the wallet name in the wallets table
        cursor.execute("""
            UPDATE wallets 
            SET wallet_name = %s 
            WHERE wallet_address = %s
        """, (new_wallet_name, wallet_address))
        conn.commit()

        if cursor.rowcount > 0:
            return True  # Wallet renamed successfully
        else:
            return False  # Wallet not found or no change made
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fetch_user_wallets(chat_id):
    """
    Fetch all wallets (wallet_name, wallet_address) for a given user by chat_id.
    
    :param chat_id: The chat ID of the user
    :return: A list of tuples (wallet_name, wallet_address) or an empty list if no wallets found
    """
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Fetch all wallets for the user
        cursor.execute("""
            SELECT wallet_name, wallet_address 
            FROM wallets 
            INNER JOIN users ON wallets.user_id = users.user_id 
            WHERE users.chat_id = %s
        """, (chat_id,))
        
        # Fetch the result
        wallets = cursor.fetchall()
        return wallets  # List of (wallet_name, wallet_address)

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def save_token_wallet(chat_id, token_address, wallet_name):
    try:
        # Create a new database connection
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Check if the user exists in the users table by chat_id
        cursor.execute("SELECT user_id FROM users WHERE chat_id = %s", (chat_id,))
        user = cursor.fetchone()
        cursor.fetchall()  # Ensure all results are fetched to avoid unread result errors

        if user is None:
            # If the user does not exist, insert the user first
            cursor.execute("INSERT INTO users (chat_id) VALUES (%s)", (chat_id,))
            conn.commit()

            # Retrieve the newly inserted user_id
            user_id = cursor.lastrowid
            print(f"Inserted new user with user_id: {user_id}")
        else:
            # User already exists, retrieve the user_id
            user_id = user[0]

        # Check if user_id is valid before inserting into wallets
        if user_id is None:
            raise ValueError("Failed to retrieve or insert user_id")

        # Check if the wallet already exists for this user
        cursor.execute("SELECT wallet_address FROM wallets WHERE user_id = %s AND wallet_address = %s", (user_id, token_address))
        wallet = cursor.fetchone()
        cursor.fetchall()  # Ensure all results are fetched

        if wallet is not None:
            # If the wallet exists, return "Exist" without inserting
            print("Wallet already exists for this user.")
            return "Exist"

        # Insert the wallet if it doesn't already exist
        print(f"Inserting wallet for user_id: {user_id}")
        cursor.execute(
            "INSERT INTO wallets (user_id, wallet_address, wallet_name) VALUES (%s, %s, %s)",
            (user_id, token_address, wallet_name)
        )
        conn.commit()
        print("Wallet inserted successfully")
        return "Inserted"

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    except ValueError as ve:
        print(f"ValueError: {ve}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
# ======================== utils ================================= #

def is_valid_sui_address(address: str) -> bool:
    # Remove '0x' prefix if present
    if address.startswith('0x'):
        address = address[2:]
    
    # Check if the address is a valid hexadecimal string
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    
    # Sui addresses are typically 64 characters long (32 bytes)
    if len(address) == 64 and hex_pattern.match(address):
        return True
    else:
        return False

# Function to format amounts
def format_amount(amount):
    # Truncate to two decimal places without rounding
    truncated_amount = int(amount * 100) / 100.0
    return f"{truncated_amount:+.2f}"

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

def get_log(owner_address):
    url = f"https://api.blockberry.one/sui/v1/accounts/{owner_address}/activity?size=20&orderBy=DESC"
    # api_key = random.choice(keys)
    headers = {
        "accept": "*/*",
        "x-api-key": 'XYxEyo08B6FZ6ulFvOznTnhoPZvD0O'
    }
    response = requests.get(url, headers=headers)
    with open('h.json','w')as file:
        json.dump(response.json(),file,indent=4)
    return response.json()

## =================== functionality ================================== #

import asyncio
import traceback
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import mysql.connector

async def monitor_transactions(wallets, context):
    """Monitor wallets and send a message for each new transaction."""
    logged_signatures = set()

    try:
        while True:
            for wallet in wallets:
                address = wallet['address']
                user_id = wallet['user_id']
                chat_id = wallet['chat_id']
                name = wallet['name']
                parsed_data = get_log(address)  # Replace with actual data fetching logic
                if "content" in parsed_data and parsed_data["content"]:
                    for item in reversed(parsed_data['content'][:3]):
                        activity_type = item.get("activityType")
                        print(item)
                        if activity_type == 'Swap':
                            details_dto = item.get("details", {}).get("detailsDto", {})
                            tx_hash = details_dto.get("txHash")
                            if tx_hash not in logged_signatures:
                                logged_signatures.add(tx_hash)
                                await send_transaction_message(details_dto, address, name, activity_type, chat_id, context)
                        elif activity_type in ['Receive', 'Send']:
                            tx_hash = item.get("details", {}).get("detailsDto", {}).get("txHash")
                            if tx_hash not in logged_signatures:
                                logged_signatures.add(tx_hash)
                                print(item)

                                await send_transaction_message(item['details']['detailsDto'], address, name, activity_type, chat_id, context)
            await asyncio.sleep(5)  # Non-blocking sleep to avoid overload

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

async def send_transaction_message(details_dto, address, name, activity_type, chat_id, context):
    """Send a formatted message to the user based on transaction details."""
    try:
        coins = details_dto.get("coins", [])
        amounts = [coin.get("amount") for coin in coins]
        symbols = [coin.get("symbol") for coin in coins]
        coin_type = [coin.get("coinType") for coin in coins]

        try:
            mkt1 = special_format(get_mkt(coin_type[0]))
        except Exception:
            mkt1 = 'N/A'

        txn = f"<a href='https://suiscan.xyz/mainnet/tx/{details_dto.get('txHash')}'>TXN</a>"
        sign = f"<a href='https://suiscan.xyz/mainnet/account/{address}'>{address[:7]}...{address[-4:]}</a>"

        message = (
            f"<b>🧮Wallet Name: </b> {name}\n\n"
            f"<b>✅Activity: </b> {activity_type}\n\n"
            f"💰<code>{format_amount(amounts[0])}</code> <b>{symbols[0]}</b> ({mkt1} Mcap)\n"
            f"👤:{sign}\n"
            f"💵{txn}"
        )

        print(message)

        await context.bot.send_message(chat_id, message, parse_mode='HTML', disable_web_page_preview=True)

    except Exception as e:
        print(f"Error occurred while sending message: {e}")


def get_wallets_for_monitoring():
    """Retrieve wallets for monitoring from the database."""
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.chat_id, w.wallet_address AS address, w.wallet_name AS name
        FROM wallets w
        JOIN users u ON w.user_id = u.user_id
    """)
    wallets = cursor.fetchall()
    cursor.close()
    connection.close()
    return wallets


async def start_monitoring(context):
    """Start monitoring transactions for all wallets."""
    wallets = get_wallets_for_monitoring()
    await monitor_transactions(wallets, context)



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


    elif query.data == 'cancel':
        await context.bot.delete_message(chat_id=chat_id,message_id=original_message_id)

    elif query.data == 'skip':
        btn2= InlineKeyboardButton("✏️Edit wallet", callback_data='edit_wallet')
        btn9= InlineKeyboardButton("➕ Add More to Main", callback_data='add_wallet')
        row2= [btn2]
        row9= [btn9]
        reply_markup = InlineKeyboardMarkup([row2,row9])
        token_address = context.user_data.get('token_address')
        wallet_name = token_address[:6]
        message = f'''Wallet {wallet_name} has been added to Main watchlist!
You can customize wallet in Wallet settings.'''
        # save_token_wallet(chat_id, token_address, wallet_name)       
        await context.bot.send_message(chat_id = chat_id,text =message,reply_markup=reply_markup,parse_mode='HTML',disable_web_page_preview=True)


    elif query.data == 'edit_wallet':
        """List all wallets for the user as inline keyboard."""
        # chat_id = update.effective_chat.id
        
        # Fetch wallets using the database function
        wallets = fetch_user_wallets(chat_id)

        if not wallets:
            await context.bot.send_message(chat_id,"No wallets found for this user.")
            return
        
        message_text = (
                f"✅ Emoji Wallet Tracker\n\n"
                f"✏️Select a wallet:"
            )
        # Create inline keyboard buttons for each wallet
        keyboard = [
            [InlineKeyboardButton(f"✅{wallet_name}", callback_data=f"wallet_{index}")]
            for index, (wallet_name, wallet_address) in enumerate(wallets)
        ]

        # Create the markup and send it to the user
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id,text=message_text, reply_markup=reply_markup)
        
    elif query.data == 'delete': 
        # Retrieve the selected wallet address from user_data
        index = context.user_data.get('wallet_index')
        chat_id = update.effective_chat.id  # Get the chat ID to identify the user
        
        if index is None:
            await update.message.reply_text("No wallet selected for renaming.")
            return
        user_id = fetch_user_id_by_chat_id(chat_id)
        wallets = fetch_user_wallets(chat_id)
        if index < len(wallets):
            wallet_name, wallet_address = wallets[index]
            # Call the function to delete the wallet from the database
            if delete_wallet_from_db(wallet_address, user_id):  # Your delete wallet function
                await query.message.reply_text(f"Wallet '{wallet_address}' deleted successfully.")
            else:
                await query.message.reply_text("Failed to delete the wallet. Please try again.")
            # Clear the selected wallet address from user_data
            context.user_data.pop('wallet_index', None)
        else:
            await query.message.reply_text("No wallet address found.")
        
    else:
        keyboard = [
                [
                    InlineKeyboardButton(text="✏️Rename", callback_data="rename"),
                    InlineKeyboardButton(text="🗑️Delete", callback_data="delete")
                ]
            ]
            # Create an inline keyboard markup
        reply_markup = InlineKeyboardMarkup(keyboard)
        wallets = fetch_user_wallets(chat_id)
        index = int(query.data.split("_")[1])
    # Get the wallet address based on the index
        if index < len(wallets):
            wallet_name, wallet_address = wallets[index]
            await context.bot.send_message(chat_id, text = f"Wallet name: {wallet_name}\nWallet address: {wallet_address}",reply_markup=reply_markup)
            context.user_data['wallet_index'] = index
        else:
            await query.edit_message_text("Invalid selection.")

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


async def wallets(update:Update, context:ContextTypes.DEFAULT_TYPE):
    """List all wallets for the user as inline keyboard."""
    chat_id = update.effective_chat.id
    
    # Fetch wallets using the database function
    wallets = fetch_user_wallets(chat_id)

    if not wallets:
        await update.message.reply_text("No wallets found for this user.")
        return
    
    message_text = (
            f"✅ Emoji Wallet Tracker\n\n"
            f"✏️Select a wallet:"
        )
    # Create inline keyboard buttons for each wallet
    keyboard = [
        [InlineKeyboardButton(f"✅{wallet_name}", callback_data=f"wallet_{index}")]
        for index, (wallet_name, wallet_address) in enumerate(wallets)
    ]

    # Create the markup and send it to the user
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=message_text, reply_markup=reply_markup)

async def handle_message(update:Update,context:ContextTypes):
    chat_id = update.message.chat_id
    message_text = update.message.text
    
    if 'state' in context.user_data:
        if context.user_data['state'] == ADD:
            context.user_data['token_address'] = message_text
            if is_valid_sui_address(context.user_data['token_address']):
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
        elif context.user_data['state'] == NAME:
            wallet_name = message_text
            token_address = context.user_data.get('token_address')
            print(token_address)
            if token_address:
                try:
                    done =save_token_wallet(chat_id, token_address, wallet_name)
                    if done != 'Exist':
                        btn2= InlineKeyboardButton("✏️Edit wallet", callback_data='edit_wallet')
                        btn9= InlineKeyboardButton("➕ Add More to Main", callback_data='add_wallet')
                        row2= [btn2]
                        row9= [btn9]
                        reply_markup = InlineKeyboardMarkup([row2,row9])
                        await context.bot.send_message(chat_id=chat_id, text=f"✅ Your wallet information has been saved with the name '{wallet_name}'.",reply_markup=reply_markup)
                        context.user_data.clear()
                        await start_monitoring(context)
                    else:
                        message = f'''❌Wallet "{context.user_data['token_address']}" already Exists!'''
                        await context.bot.send_message(chat_id = chat_id,text =message,parse_mode='HTML',disable_web_page_preview=True)
                except IndexError:
                    await context.bot.send_message(
                chat_id=chat_id,
                text="❌ An error occurred while saving your wallet or Wallet already Exist. Please try again."
            )
                context.user_data.clear()  # Clear user data after saving
            else:
                await context.bot.send_message(chat_id=chat_id, text='Token address not found. Please restart the process.')

        elif context.user_data['state'] == WALLET:
            new_wallet_name = update.message.text
            # Retrieve the wallet index from the context
            index = context.user_data.get('wallet_index')
            if index is None:
                await update.message.reply_text("No wallet selected for renaming.")
                return
            # Fetch wallets to get the wallet address (for confirmation or validation if needed)
            wallets = fetch_user_wallets(chat_id)
            
            if index < len(wallets):
                wallet_name, wallet_address = wallets[index]

                # Call the function to rename the wallet in the database
                if rename_wallet_in_db(wallet_address, new_wallet_name):
                    await update.message.reply_text(f"Wallet '{wallet_name}' renamed to '{new_wallet_name}' successfully.")
                else:
                    await update.message.reply_text("Failed to rename the wallet. Please try again.")
            else:
                await update.message.reply_text("Invalid wallet index.")
            # Clear the wallet index from user_data
            context.user_data.pop('wallet_index', None)
# TOKEN_KEY_ = '7580227168:AAE8jOiX1vhwFemiZ5K29ixATQ2fNZCGRuQ'
TOKEN_KEY_ = '7112307264:AAHpaP5uZfU8bYb0pVE7j7WWnVLBQzejLvA'

def main():
    app = ApplicationBuilder().token(TOKEN_KEY_).post_init(lambda app: app.job_queue.start()).build()
    # start_monitoring_thread(app)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("wallets", wallets))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CallbackQueryHandler(button_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
if __name__ == '__main__':
    main()