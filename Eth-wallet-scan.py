import time
import requests
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Stylish banner with program info
print(Fore.GREEN + Style.BRIGHT + """
====================================================
               E T H   W A L L E T   S C A N N E R               
          Created by """ + Fore.RED + """
 ________  _______   ___       _______   ________   ________  ________     
|\   ____\|\  ___ \ |\  \     |\  ___ \ |\   ___  \|\   __  \|\   __  \    
\ \  \___|\ \   __/|\ \  \    \ \   __/|\ \  \\ \  \ \  \|\  \ \  \|\  \   
 \ \  \    \ \  \_|/_\ \  \    \ \  \_|/_\ \  \\ \  \ \  \\\  \ \   _  _\  
  \ \  \____\ \  \_|\ \ \  \____\ \  \_|\ \ \  \\ \  \ \  \\\  \ \  \\  \| 
   \ \_______\ \_______\ \_______\ \_______\ \__\\ \__\ \_______\ \__\\ _\ 
    \|_______|\|_______|\|_______|\|_______|\|__| \|__|\|_______|\|__|\|__| 
""" + Style.RESET_ALL + Fore.GREEN + """
                   Telegram: """ + Fore.CYAN + """@celenor""" + Style.RESET_ALL + Fore.GREEN + """
====================================================
""" + Style.RESET_ALL)

# Requesting user's Etherscan API key
api_key = input(Fore.CYAN + "Please enter your Etherscan API key: " + Style.RESET_ALL)

# Output file for wallets above one dollar
output_file = "wallets_above_one_dollar.txt"

# Function to get the current price of Ethereum in USD
def get_eth_price():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd")
        data = response.json()
        eth_price = data['ethereum']['usd']
        print(Fore.CYAN + f"Current Ethereum price: ${eth_price:.2f} USD")
        return eth_price
    except Exception as e:
        print(Fore.RED + "Error retrieving Ethereum price:", e)
        return 2000  # Default price in case of error

# Function to check balance and store if valid
def check_balance_and_store(mnemonic_phrase, eth_price):
    # Generate Seed from mnemonic
    seed_generator = Bip39SeedGenerator(mnemonic_phrase)
    seed = seed_generator.Generate()

    # Create BIP44 wallet for Ethereum
    bip44_wallet = Bip44.FromSeed(seed, Bip44Coins.ETHEREUM)
    eth_account = bip44_wallet.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)

    # Extract Ethereum address
    eth_address = eth_account.PublicKey().ToAddress()

    # API request to Etherscan for balance
    etherscan_url = f"https://api.etherscan.io/api?module=account&action=balance&address={eth_address}&tag=latest&apikey={api_key}"
    response = requests.get(etherscan_url)
    data = response.json()

    if data["status"] == "1":
        # Convert balance from Wei to ETH
        balance_wei = int(data["result"])
        balance_eth = balance_wei / (10 ** 18)

        # Convert balance to USD using live Ethereum price
        dollar_value = balance_eth * eth_price

        # If balance is more than $1, save the information
        if dollar_value > 1:
            with open(output_file, "a") as f:
                f.write(f"Mnemonic: {mnemonic_phrase}\n")
                f.write(f"Address: {eth_address}\n")
                f.write(f"Balance: {balance_eth:.18f} ETH\n")
                f.write(f"Value: ${dollar_value:.2f}\n")
                f.write("-" * 40 + "\n")  # Separator line
            return 1  # Return 1 if a valid wallet is found

    return 0  # Return 0 if wallet balance is not valid

# Infinite loop to generate mnemonic phrases and check balance
mnemo = Mnemonic("english")
valid_wallet_count = 0
total_wallet_count = 0  # Total wallets checked counter

# Get live ETH price at start
eth_price = get_eth_price()

# Main program loop
try:
    while True:
        # Generate a random 12-word mnemonic phrase
        mnemonic_phrase = mnemo.generate(strength=128)  # 12 words = 128 bits
        total_wallet_count += 1  # Increment total wallets checked
        valid_wallet_count += check_balance_and_store(mnemonic_phrase, eth_price)

        # Display wallet counts in a single line with dynamic update
        print(f"\r{Fore.GREEN}Total wallets checked: {Fore.MAGENTA}{total_wallet_count} | "
              f"{Fore.GREEN}Wallets with balance > $1: {Fore.MAGENTA}{valid_wallet_count}", end="")

        # Add delay to reduce load on API
        time.sleep(1)  # Adjust time as needed

except KeyboardInterrupt:
    print("\nProgram stopped by user.")
