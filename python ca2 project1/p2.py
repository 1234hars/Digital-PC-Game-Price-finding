import csv
import re
import bcrypt
import requests
from getpass import getpass
import time
import random

# Constants
MAX_LOGIN_ATTEMPTS = 5
CSV_FILE = 'users.csv'
API_BASE_URL = 'https://www.cheapshark.com/api/1.0'

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if (len(password) < 8 or
        not re.search(r'[A-Z]', password) or
        not re.search(r'[a-z]', password) or
        not re.search(r'[0-9]', password) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        return False
    return True

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def load_users():
    users = {}
    try:
        with open(CSV_FILE, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 3:  # Ensure the row has all required fields
                    users[row[0]] = {'password': row[1], 'security_question': row[2]}
    except FileNotFoundError:
        print("Welcome! It looks like you're our first user. Let's get you set up.")
    except csv.Error as e:
        print(f"Oops! We had a little hiccup reading our user database: {e}")
    return users

def save_users(users):
    try:
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            for email, data in users.items():
                writer.writerow([email, data['password'], data['security_question']])
    except IOError as e:
        print(f"Oh no! We couldn't save your information: {e}")

def register_user():
    print("\n🎮 Welcome to Game Deal Hunter! Let's get you registered. 🎮")
    email = input("What's your email address? ")
    while not validate_email(email):
        print("Hmm, that doesn't look like a valid email. Let's try again.")
        email = input("What's your email address? ")

    password = getpass("Choose a strong password (our little secret): ")
    while not validate_password(password):
        print("Your password needs a bit more oomph! Make sure it's at least 8 characters long and includes uppercase, lowercase, numbers, and special characters.")
        password = getpass("Let's try another password: ")

    security_question = input("Give us a security question (in case you forget your password): ")
    security_answer = input("And what's the answer to that question? ")

    users = load_users()
    if email in users:
        print("Looks like you're already part of the club! Try logging in instead.")
        return

    hashed_password = hash_password(password)
    users[email] = {
        'password': hashed_password.decode('utf-8'),  # Store as string
        'security_question': f"{security_question}:{security_answer}"
    }
    save_users(users)
    print("Welcome aboard! You're all set to hunt for amazing game deals.")

def login():
    users = load_users()
    attempts = 0

    while attempts < MAX_LOGIN_ATTEMPTS:
        email = input("What's your email? ")
        password = getpass("And your super-secret password? ")

        if email in users and verify_password(password, users[email]['password'].encode('utf-8')):
            print("Welcome back, game hunter!")
            return email
        else:
            attempts += 1
            remaining = MAX_LOGIN_ATTEMPTS - attempts
            print(f"Oops! That didn't work. You have {remaining} more tries.")

    print("Sorry, we couldn't log you in. Maybe try again later?")
    exit()

def forgot_password():
    users = load_users()
    email = input("What's your email address? ")

    if email in users:
        question, answer = users[email]['security_question'].split(':')
        print(f"Here's your security question: {question}")
        user_answer = input("What's your answer? ")

        if user_answer.lower() == answer.lower():
            new_password = getpass("Great! Choose a new password: ")
            while not validate_password(new_password):
                print("Let's make that password a bit stronger. It should be at least 8 characters with uppercase, lowercase, numbers, and special characters.")
                new_password = getpass("Try another password: ")

            users[email]['password'] = hash_password(new_password).decode('utf-8')
            save_users(users)
            print("Password updated! You're back in the game.")
        else:
            print("That answer doesn't match our records. Give it another shot!")
    else:
        print("We couldn't find that email in our system. Want to register instead?")

def search_game_deals(game_name):
    print(f"Hunting for deals on {game_name}...")
    time.sleep(1)  # Add a short delay for dramatic effect
    params = {'title': game_name}
    try:
        response = requests.get(f"{API_BASE_URL}/games", params=params)
        response.raise_for_status()
        games = response.json()
        if games:
            game_id = games[0]['gameID']
            deals_response = requests.get(f"{API_BASE_URL}/deals", params={'gameID': game_id})
            deals_response.raise_for_status()
            deals = deals_response.json()
            return deals
    except requests.RequestException as e:
        print(f"Oops! We hit a snag while looking for deals: {e}")
    return None

def display_game_deals(deals):
    if not deals:
        print("Aww, we couldn't find any deals for that game. Maybe try another?")
        return

    print("\n🎉 Jackpot! Here are the deals we found: 🎉")
    for deal in deals:
        print(f"\n🕹️ {deal['title']}")
        print(f"🏪 Store: {deal['storeID']}")
        print(f"💲 Normal Price: ${deal['normalPrice']}")
        print(f"🏷️ Sale Price: ${deal['salePrice']}")
        print(f"💰 You Save: {deal['savings']}%")
        print(f"⭐ Deal Rating: {deal['dealRating']}")
        print(f"🔗 Grab it here: https://www.cheapshark.com/redirect?dealID={deal['dealID']}")

def main():
    print("🎮 Welcome to Game Deal Hunter! 🎮")
    print("Your one-stop shop for the best PC game deals!")

    while True:
        print("\nWelcome to Harsh kumar game hunting club?")
        print("\nWhat would you like to do?")
        print("1. Log in and start hunting")
        print("2. Join the hunt (Register)")
        print("3. Forgot your password?")
        print("4. Call it a day (Exit)")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            user_email = login()
            if user_email:
                print("Time to find some game deals!")
                while True:
                    game_name = input("\nWhat game are you looking for? (or type 'quit' to log out): ")
                    if game_name.lower() == 'quit':
                        print("Thanks for hunting with us. Come back soon!")
                        break
                    deals = search_game_deals(game_name)
                    display_game_deals(deals)
        elif choice == '2':
            register_user()
        elif choice == '3':
            forgot_password()
        elif choice == '4':
            print("Thanks for using Game Deal Hunter. Happy gaming!\n   ... harsh Kumar _12304437")
            break
        else:
            print("Oops! That's not a valid choice. Let's try again.")

if __name__ == "__main__":
    main()