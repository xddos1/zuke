# Instagram-reporter
This bot helps users to mass report accounts with clickbaits or objectionable material.

# DISCLAIMER: 
**This tool is provided for educational purposes only. Misuse of this tool for malicious purposes, including targeting accounts for personal grievances, is unethical and may be illegal.**  
The author assumes no responsibility for any consequences arising from the misuse of this tool.

## Installation

1. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

2. Ensure you have Google Chrome installed on your system.

3. Download the ChromeDriver that matches your Chrome version from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in a directory included in your system's PATH.

## Usage

1. Put the list of accounts with credentials in the same folder as this program and name it [acc.txt](http://_vscodecontentref_/1). The file should contain one account per line in the format [username:password](http://_vscodecontentref_/2).

2. Run the script with the following command:
    ```sh
    python report_bot.py -u <target_username> -f <path_to_acc_file>
    ```

    - `-u` or `--username`: The username of the account you want to report.
    - `-f` or `--file`: The path to the file containing the list of accounts (defaults to [acc.txt](http://_vscodecontentref_/3)).

## Telegram Bot Usage

1. Set up your [.env](http://_vscodecontentref_/4) file with the following variables:
    ```
    BOT_TOKEN=<your_telegram_bot_token>
    MONGO_URI=<your_mongodb_uri>
    ADMIN_ID=<your_telegram_user_id>
    ```

2. Start the Telegram bot:
    ```sh
    python zukes_insta.py
    ```

3. Use the following commands in the Telegram bot:
    - `/start`: Start the bot and create your user data.
    - `/help`: Show the available tools.
    - `/rules`: Display the bot usage rules.
    - `/target <username>`: Set your target username.
    - `/showconfig`: Show the current bot configuration.
    - `/logs`: Show your user logs.
    - `/acc <username:password>`: Set your account credentials.
    - `/rcode <your_gift_code_here>`: Redeem a gift code.
    - `/attack`: Initiate an attack.
    - `/gift <number_of_tokens>`: Generate a gift code (admin only).
    - `/broadcast <message>`: Broadcast a message to all users (admin only).

## Flow of working

1. User enters the username to report.
2. The bot logs in using the credentials from the list, then navigates to the Instagram page.
3. The bot reports the specified Instagram user for objectionable content.

Example:
```sh
python report_bot.py -u target_user -f acc.txt