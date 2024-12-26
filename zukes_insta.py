import random
import string
import subprocess
import threading
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext, Application, CommandHandler
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Load the admin ID from the .env file and convert to integer

# Initialize MongoDB connection
client = MongoClient(MONGO_URI)
db = client.get_database("zuke_db")
users_collection = db.users
acc_collection = db.acc  # Separate collection for account credentials
gift_codes_collection = db.gift_codes  # New collection for storing gift codes

# Fix the 'acc' field type for all users where it is a string (run only once or on bot startup)
def fix_acc_field():
    users_collection.update_many(
        {"acc": {"$type": "string"}},  # Find users where 'acc' is a string
        {"$set": {"acc": []}}  # Convert 'acc' to an empty array
    )
    print("Fixed 'acc' field type for users.")

# Call the function to fix any 'acc' field issues at the start of the bot
fix_acc_field()

# Command to start the bot
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "User"
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        users_collection.insert_one({
            "user_id": user_id,
            "acc": [],  # Initialize acc as an array
            "logs": [{"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "message": f"User {user_id} has started the bot."}],
            "target": None
        })

    welcome_message = (
        f"Welcome, {first_name}!\n"
        "Use /help to see the available tools.\n"
        "Review the rules: /rules\n\n"
        "Need support? Email us at hey@xodivorce.in"
    )
    await update.message.reply_text(welcome_message)

# Command to show help menu with the new /attack command included
async def help_menu(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Count how many accounts the user has added in the 'acc' collection
    user_accounts = acc_collection.count_documents({"user_id": user_id})
    
    # If user is admin, give unlimited tokens
    if user_id == ADMIN_ID:
        tokens = "Unlimited"
        admin_commands = "\nAdmin Commands:\n/gift <number_of_tokens> - Generate a gift code.\n/broadcast <your_message> - Send a broadcast to users."  # Admin-only help message
    else:
        # Retrieve the current token count from the users collection
        user_data = users_collection.find_one({"user_id": user_id})
        tokens = user_data.get("tokens", 0)  # Default to 0 if no tokens are found
        admin_commands = ""  # No admin commands for regular users

    help_message = (
        f"Here are the available tools:\n"
        f"/target <username> - Set your target username.\n"
        f"/showconfig - Show the current bot configuration.\n"
        f"/logs - Show your user logs.\n"
        f"/acc <username:password> - Set your account credentials.\n"
        f"/rcode <your_gift_code_here> - Redeem a gift code.\n"
        f"/attack - Initiate an attack.\n"  # New /attack command added here
        f"Tokens: {tokens}\n"  # Show the token count message
        f"{admin_commands}"  # Add admin commands if applicable
    )
    await update.message.reply_text(help_message)

# Command to display rules
async def rules(update: Update, context: CallbackContext) -> None:
    rules_message = (
        "Bot Usage Rules:\n\n"
        "1.How to Gain Tokens for Free:\n"
            "- For every 10 accounts you add, you will earn 1 token.\n"
            "- Admins can gift you generate gift codes to award tokens.\n"
        "2. The bot is provided as-is, and we do not take responsibility for any misuse or consequences arising from its use.\n"
        "3. You are solely responsible for adhering to the laws and regulations of your country while using this bot.\n"
        "4. Misuse of the bot for illegal or unethical activities is strictly prohibited.\n"
        "5. We reserve the right to suspend or ban users for violations of these rules.\n"
        "6. Use this bot at your own risk. The developers assume no liability for any damages caused by the bot's usage.\n\n"
        "- By using this bot, you agree to these rules and disclaimers."
    )
    await update.message.reply_text(rules_message)

# Command to set target username
async def target(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await update.message.reply_text("You must start the bot first to create your user data.")
        return

    if context.args:
        username = context.args[0].strip()

        # Check if the target is already set to the provided username
        current_target = user_data.get("target")
        if current_target == username:
            await update.message.reply_text(f"Your target is already set to {username}.")
            return

        # Update the target username in the database
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"target": username}}
        )

        # Log the action of setting the target username
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"logs": {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "message": f"Set target username to {username}"}}}
        )

        # Send confirmation message
        await update.message.reply_text(f"Target username successfully set to: {username}")
    else:
        await update.message.reply_text("Usage: /target <username>")

# Command to show current configuration
async def show_config(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await update.message.reply_text("You must start the bot first to create your user data.")
        return

    target_data = user_data.get("target", "None")
   
    config_data = (
        f"User ID: {user_id}\n"
        f"Target username: {target_data}\n"
    )

    await update.message.reply_text(f"Your Current Configuration:\n{config_data}")

# Command to show user logs
async def logs(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await update.message.reply_text("You must start the bot first to create your user data.")
        return

    logs_data = "\n".join([f"{log['timestamp']} - {log['message']}" for log in user_data["logs"]])

    if logs_data:
        await update.message.reply_text(f"Your Logs:\n{logs_data}")
    else:
        await update.message.reply_text("You have no logs yet.")

async def acc(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await update.message.reply_text("You must start the bot first to create your user data.")
        return

    if context.args:
        # Expect the format username:password
        acc_info = context.args[0].strip()
        if ':' not in acc_info:
            await update.message.reply_text("Usage: /acc <username:password>")
            return

        username, password = acc_info.split(':', 1)

        # Validate the username length (minimum 6 characters)
        if len(username) < 6:
            await update.message.reply_text("Invalid username. Please enter a valid username.")
            return
        
        # Validate the password length (minimum 6 characters)
        if len(password) < 6:
            await update.message.reply_text("Invalid password. Please enter a valid password.")
            return

        # Check if the account already exists for this user
        existing_account = acc_collection.find_one({"user_id": user_id, "username": username})
        if existing_account:
            await update.message.reply_text("This account already exists. Please enter a different account:password.")
            return

        # Store the account information in the users collection (acc array)
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"acc": f"{username}:{password}"}}  # Add new account data to the array
        )

        # Store the account information in the acc collection (separate collection)
        acc_collection.insert_one({
            "user_id": user_id,  # Link the account to the user ID
            "username": username,
            "password": password,
        })

        # Count the total number of accounts added by the user
        account_count = acc_collection.count_documents({"user_id": user_id})

        # Award tokens for every 10 accounts added
        if account_count % 10 == 0:  # Check if the user has added a multiple of 10 accounts
            users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"tokens": 1}}  # Increment tokens by 1
            )
            await update.message.reply_text(f"Congratulations! You have added {account_count} accounts and earned 1 token.")

        # Log the action of setting the account information
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"logs": {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "message": f"Set account information for {username}."}}}
        )

        # Send confirmation message
        await update.message.reply_text(f"Account information for {username} successfully set.")
    else:
        await update.message.reply_text("Usage: /acc <username:password>")

# Command to generate a gift code (admin only)
async def gift(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    if context.args:
        try:
            # Get the number of tokens to assign
            tokens = int(context.args[0])
            if tokens <= 0:
                await update.message.reply_text("The number of tokens must be a positive integer.")
                return
        except ValueError:
            await update.message.reply_text("Usage: /gift <number_of_tokens>")
            return

        # Generate an 8-character gift code (uppercase letters and digits)
        gift_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Store the gift code in the database with the token count and usage status
        gift_codes_collection.insert_one({
            "gift_code": gift_code,
            "tokens": tokens,
            "used_by": None  # No one has used it yet
        })

        # Log the gift code generation in the admin's logs
        users_collection.update_one(
            {"user_id": ADMIN_ID},
            {"$push": {"logs": {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "message": f"Generated gift code {gift_code} with {tokens} tokens."}}}
        )

        await update.message.reply_text(
            f"Gift code `{gift_code}` generated successfully! It provides {tokens} tokens.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("Usage: /gift <number_of_tokens>")

# Command for users to redeem a gift code
async def rcode(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if context.args:
        gift_code = context.args[0].strip()

        # Check if the gift code exists in the database
        gift_data = gift_codes_collection.find_one({"gift_code": gift_code})

        if not gift_data:
            await update.message.reply_text("Invalid gift code.")
            return

        if gift_data["used_by"]:
            await update.message.reply_text("This gift code has already been redeemed.")
            return

        # Mark the gift code as used and assign the tokens to the user
        gift_codes_collection.update_one(
            {"gift_code": gift_code},
            {"$set": {"used_by": user_id}}  # Set the user_id who used the code
        )

        # Add tokens to the user (first-come, first-serve)
        users_collection.update_one(
            {"user_id": user_id},
            {"$inc": {"tokens": gift_data["tokens"]}}  # Increment the user's tokens by the number from the gift code
        )

        # Log the redemption
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"logs": {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "message": f"Redeemed gift code {gift_code} for {gift_data['tokens']} tokens."}}}
        )

        await update.message.reply_text(f"Gift code redeemed successfully! You received {gift_data['tokens']} tokens.")
    else:
        await update.message.reply_text("Usage: /rcode <gift_code>")

# Global lock variable
attack_in_progress = False
attack_lock = threading.Lock()

async def attack(update: Update, context: CallbackContext) -> None:
    global attack_in_progress

    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await update.message.reply_text("You must start the bot first to create your user data.")
        return

    # Retrieve target username from the user's data
    target_username = user_data.get("target")
    
    if not target_username:
        await update.message.reply_text("You must set a target username first using /target <username>.")
        return

    # Check if the server is currently processing an attack
    if attack_in_progress:
        await update.message.reply_text("Server busy, please try again in 1 hour.")
        return

    # Notify the user that the attack is being processed
    await update.message.reply_text(f"Processing your attack on {target_username}.\nIt can take several minutes :)\n\nWe will notify you once the attack is complete.")

    # Lock the server to prevent multiple attacks at once
    with attack_lock:
        # Set the lock to True indicating an attack is in progress
        attack_in_progress = True

        # Check if the user is the admin (admin has unlimited tokens)
        if user_id == ADMIN_ID:
            current_tokens = "Unlimited"
        else:
            # Check how many tokens the user has (regular user case)
            current_tokens = user_data.get("tokens", 0)

            if current_tokens <= 0:
                await update.message.reply_text("You don't have enough tokens to perform an attack.")
                attack_in_progress = False  # Unlock the server if the attack fails
                return

            # Deduct 1 token from the user (regular user case)
            users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"tokens": -1}}  # Decrease token count by 1
            )

        # Log the attack attempt
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"logs": {"timestamp": timestamp, "message": f"Initiated an attack on {target_username}"}}}
        )

        # Example of triggering the Selenium script
        try:
            # Run the Selenium script as a subprocess, passing the target username from the DB
            process = subprocess.Popen(
                ['python3', 'report_bot.py', '-u', target_username],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                # Successful execution
                await update.message.reply_text(f"The attack on {target_username} has been initiated at {timestamp}.\n 1 token has been deducted.")
            else:
                # Error running the script
                await update.message.reply_text(f"Error initiating attack: {stderr.decode()}")

        except Exception as e:
            await update.message.reply_text(f"An error occurred while initiating the attack: {str(e)}")
        
        # Unlock the server after the attack completes
        attack_in_progress = False


# Command to broadcast a message to all users (admin only)
async def broadcast(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("You do not have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    # Get the broadcast message from the command arguments
    broadcast_message = " ".join(context.args).strip()

    # Fetch all user IDs from the database
    users = users_collection.find({}, {"user_id": 1})
    user_ids = [user["user_id"] for user in users]

    success_count = 0
    failure_count = 0

    # Send the message to all users
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=broadcast_message)
            success_count += 1
        except Exception as e:
            print(f"Failed to send message to {uid}: {str(e)}")
            failure_count += 1

    # Log the broadcast event in the admin's logs
    users_collection.update_one(
        {"user_id": ADMIN_ID},
        {"$push": {"logs": {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "message": f"Broadcasted message: {broadcast_message}"}}}
    )

    # Send a confirmation message to the admin
    await update.message.reply_text(
        f"Broadcast complete. Successfully sent to {success_count} users. Failed to send to {failure_count} users."
    )


# Function to start the bot
def start_bot():
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is not defined. Please check your .env file.")
        return

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_menu))
    application.add_handler(CommandHandler("rules", rules))  # Register the /rules command
    application.add_handler(CommandHandler("target", target))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("showconfig", show_config))
    application.add_handler(CommandHandler("broadcast", broadcast))  # Register the /broadcast command for admin
    application.add_handler(CommandHandler("logs", logs))  # Register the new /logs command
    application.add_handler(CommandHandler("acc", acc))  # Register the new /acc command
    application.add_handler(CommandHandler("gift", gift))  # Register the new /gift command for admin
    application.add_handler(CommandHandler("rcode", rcode))  # Register the new /rcode command for users

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    print("Starting Telegram bot...")
    start_bot()
