import random as rd
import numpy as np
import sqlite3 as sql

def generate_card_number():
    card_number_exc_check = f"400000{rd.randint(0, 999999999):09}"
    card_number_array = np.array(list(int(digit) for digit in card_number_exc_check))
    card_number_array[::2] = card_number_array[::2] * 2
    card_number_array = np.where(card_number_array > 9, card_number_array - 9, card_number_array)
    card_number_sum = np.sum(card_number_array)
    #print(card_number_sum)
    if card_number_sum % 10 != 0:
        checksum = str(10 - card_number_sum % 10)
    else:
        checksum = "0"
    return card_number_exc_check + checksum

def validate_card_number(card_number_to_validate):
    card_number_array = np.array(list(int(digit) for digit in card_number_to_validate))
    #card_number_sum = np.sum(card_number_array)
    #if card_number_sum % 10 != 0:
    #    return False
    card_number_check = card_number_array[-1]
    card_number_exc_check = card_number_array[:-1]
    card_number_exc_check[::2] = card_number_exc_check[::2] * 2
    card_number_exc_check = np.where(card_number_exc_check > 9, card_number_exc_check - 9, card_number_exc_check)
    card_number_exc_check_sum = np.sum(card_number_exc_check)
    if (card_number_exc_check_sum + card_number_check) % 10 != 0:
        return False
    else:
        return True

def transfer_balance():
    print("Transfer")
    target_card_number = input("Enter card number:")
    # check if this is own card number
    if target_card_number == card_number:
        print("You can't transfer money to the same account!")
        return
    # test for luhn algorithm
    if not validate_card_number(target_card_number):
        print("Probably you made a mistake in the card number. Please try again!")
        return
    cur.execute(f"SELECT * FROM card WHERE number = '{target_card_number}';")
    target_exists = cur.fetchone()
    if not target_exists:
        print("Such a card does not exist.")
        return
    transfer_amount = int(input("Enter how much money you want to transfer:"))
    if transfer_amount > get_current_balance():
        print("Not enough money!")
        return
    cur.execute(f"UPDATE card SET balance = balance + {transfer_amount} WHERE number = '{target_card_number}';")
    cur.execute(f"UPDATE card SET balance = balance - {transfer_amount} WHERE number = '{card_number}';")
    conn.commit()
    print("Success!)")
    return

def get_current_balance():
    cur.execute(f"SELECT balance FROM card WHERE number = '{card_number}' AND pin = '{pin}'")
    return cur.fetchone()[0]

def logged_in_session():
    currently_logged_in = True
    print("You have successfully logged in!")
    while currently_logged_in:
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")

        account_holder_choice = int(input())

        if account_holder_choice == 1:
            #cur.execute(f"SELECT balance FROM card WHERE number = '{card_number}' AND pin = '{pin}'")
            #balance = cur.fetchone()
            #print(f"Balance: {balance[0]}")
            print(f"Balance: {get_current_balance()}")

        elif account_holder_choice == 2:
            income_amount = int(input("Enter income:"))
            cur.execute(f"UPDATE card SET balance = balance + {income_amount} WHERE number = '{card_number}';")
            conn.commit()
            print("Income was added!")

        elif account_holder_choice == 3:
            transfer_balance()

        elif account_holder_choice == 4:
            cur.execute(f"DELETE FROM card WHERE number = '{card_number}';")
            conn.commit()
            print("The account has been closed!")
            currently_logged_in = False

        elif account_holder_choice == 5:
            currently_logged_in = False
            print("You have successfully logged out")

        else:
            currently_logged_in = False
            exit()

#stored_details = np.array([["0", "0"]])
end_process = False
conn = sql.connect('card.s3db')
cur = conn.cursor()
# cur.execute("DROP TABLE IF EXISTS card")
# conn.commit()
cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")
conn.commit()

while not end_process:

    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    choice = int(input())

    #print(stored_details)

    if choice == 1:
        card_number = generate_card_number()
        pin = f"{rd.randint(0, 9999):04}"
        #details = (card_number, pin)
        #stored_details = np.append(stored_details, [details], axis=0)
        cur.execute(f"INSERT INTO card (number, pin) VALUES ('{card_number}', '{pin}');")
        conn.commit()
        print("Your card has been created")
        print("Your card number:")
        print(card_number)
        print("Your card PIN:")
        print(pin)

        #print(stored_details)
        #print(type(stored_details))

    elif choice == 2:
        card_number = input("Enter your card number:")
        pin = input("Enter your card PIN:")
        #search_value = (card_number, pin)
        #exists = np.any(np.all(stored_details == np.array(search_value), axis=1))
        # idx = np.where((stored_details == search_value).all(axis=1))[0]
        cur.execute(f"SELECT * FROM card WHERE number = '{card_number}' AND pin = '{pin}';")
        exists = cur.fetchone()
        if exists:
            logged_in_session()
        else:
            print("Wrong card number or PIN!")

    else:
        end_process = True
        exit()

