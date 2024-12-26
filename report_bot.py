from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import argparse
import sys
import time
import os

# Command-line argument parser
def getOptions(args=sys.argv[1:]):
    """
    Parse command-line arguments to get username.
    """
    parser = argparse.ArgumentParser(description="This bot helps users interact with Instagram accounts.")
    parser.add_argument("-u", "--username", type=str, default="", help="Username to target.")
    options = parser.parse_args(args)
    return options

# Get arguments
args = getOptions()
target_username = args.username

# Prompt user for username if not provided via command-line
if target_username == "":
    target_username = input("Username: ")

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set.")

try:
    client = MongoClient(MONGO_URI)
    db = client['zuke_db']  
    collection = db['acc']
    print("Connected to MongoDB successfully.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    sys.exit(1)

# Fetch account credentials from the database
try:
    credentials = list(collection.find({}, {"_id": 0, "username": 1, "password": 1}))
    print(f"Fetched credentials: {credentials}")

    if not credentials:
        print("No credentials found in the database.")
        sys.exit(1)
except Exception as e:
    print(f"Error fetching credentials from MongoDB: {e}")
    sys.exit(1)

# Loop through each set of credentials
for account in credentials:
    un = account["username"]
    pw = account["password"]

    try:
        # Set up the WebDriver
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        web = webdriver.Chrome(service=service, options=options)

        # Go to Instagram login page
        web.get("https://www.instagram.com/accounts/login/")

        # Wait for the login elements and enter credentials
        WebDriverWait(web, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        web.find_element(By.NAME, 'username').send_keys(un)
        web.find_element(By.NAME, 'password').send_keys(pw)
        web.find_element(By.NAME, 'password').send_keys(Keys.RETURN)
        time.sleep(5)  # Wait for the page to load after login

        # Navigate to the target user's profile
        try:
            web.get(f"https://www.instagram.com/{target_username}/")
            WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, f"//a[contains(@href, '/{target_username}/')]")))
            print(f"Opened profile page for {target_username}")
        except Exception as e:
            print(f"Error opening profile page for {target_username}: {e}")

        # Locate and click the three-dot menu
        try:
            three_dot_button = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(@class, "x1i10hfl x972fbf xcfux6l x1qhh985 xm0m39n x9f619")]')
                )
            )
            three_dot_button.click()
            print("Clicked on the three-dot menu in the target profile.")
        except Exception as e:
            print(f"Error clicking the three-dot menu: {e}")

        # Delay before clicking the "Report" button
        try:
            report_button = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="Report"]'))
            )
            report_button.click()
            print("Clicked the 'Report' button successfully.")
            time.sleep(5)  # Wait for 5 seconds after clicking
        except Exception as e:
            print(f"Error clicking the 'Report' button: {e}")

        # Locate and click the "Report Account" option
        try:
            report_account = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(text(), "Report Account") and contains(@class, "x9f619 xjbqb8w")]')
                )
            )
            report_account.click()
            print("Clicked on the Report Account option in the target profile.")
        except Exception as e:
            print(f"Error clicking the Report Account option: {e}")

        # Locate and click the "Shouldn't Be on Instagram" option
        try:
            not_account = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(text(), "It\'s posting content that shouldn\'t be on Instagram") and contains(@class, "x9f619")]')
                )
            )
            not_account.click()
            print("Clicked on the Shouldn't Be on Instagram option in the target profile.")
        except Exception as e:
            print(f"Error clicking the Shouldn't Be on Instagram option: {e}")

        #if Locate and click the "Sale of illegal or regulated goods" option
        try:
            illegal_account = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(text(), "Sale of illegal or regulated goods") and contains(@class, "x9f619")]')
                )
            )
            illegal_account.click()
            print("Clicked on the Sale of illegal or regulated goods in the target profile.")
        except Exception as e:
            print(f"Error clicking the Sale of illegal or regulated goods option: {e}")

        #else Locate and click the "Selling or promoting restricted items" option
        try:
            illegal_accountt = WebDriverWait(web, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(text(), "Selling or promoting restricted items") and contains(@class, "x9f619")]')
                )
            )
            illegal_accountt.click()
            print("Clicked on the Selling or promoting restricted items in the target profile.")
        except Exception as e:
            print(f"Error clicking the Selling or promoting restricted items option: {e}")

        #if Locate and click the "Drugs" button
        try:
            drug_button = WebDriverWait(web, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[contains(@class, "_abn2") and text()="Drugs"]')
                )
            )
            drug_button.click()
            print("Clicked on the 'Drugs' option successfully.")
        except Exception as e:
            print(f"Error clicking the 'Drugs' option: {e}")

        #else Locate and click the "Drugs" button
        try:
            drug_buttonn = WebDriverWait(web, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "x9f619") and contains(@class, "xjbqb8w") and text()="Drugs"]')
            )
            )
            drug_buttonn.click()
            print("Clicked on the 'Drugs' button successfully.")
        except Exception as e:
            print(f"Error clicking the 'Drugs' button: {e}")

        #then Locate and click the "Highly addictive drugs like cocaine, heroin or fentanyl" button
        try:
            drug_buttonn = WebDriverWait(web, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class, "x9f619") and contains(@class, "xjbqb8w") and text()="Highly addictive drugs like cocaine, heroin or fentanyl"]')
            )
            )
            drug_buttonn.click()
            print("Clicked on the 'Highly addictive drugs like cocaine, heroin or fentanyl' button successfully.")
        except Exception as e:
            print(f"Error clicking the 'Highly addictive drugs like cocaine, heroin or fentanyl' button: {e}")


        # Wait until the "Submit report" button is enabled and click it
        try:
            submit_button = WebDriverWait(web, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(@class, "_acan") and text()="Submit report"]')
                )
            )
            submit_button.click()
            print("Clicked on the 'Submit report' button successfully.")
            time.sleep(5)  # Wait for 5 seconds after clicking
        except Exception as e:
            print(f"Error clicking the 'Submit report' button: {e}")

        # Logout process
        try:
            WebDriverWait(web, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label, "Account")]'))).click()
            WebDriverWait(web, 5).until(EC.presence_of_element_located((By.XPATH, '//*[text()="Log Out"]'))).click()
            print("Logged out successfully")
        except Exception as e:
            print(f"Force logout")

    except Exception as e:
        print(f"Unexpected error during execution: {e}")

    finally:
        # Quit the browser after processing
        web.quit()
        print("Browser closed. Proceeding to the next account (if available).")


