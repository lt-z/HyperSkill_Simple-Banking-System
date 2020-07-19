from random import randint
import sqlite3


class Bank:
    def __init__(self):
        self.logged_in = False
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.create_table()
        self.menu()

    def create_table(self):
        sql_create_card_table = """CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT,
        pin TEXT, balance INTEGER DEFAULT 0);"""
        self.cur.execute(sql_create_card_table)
        self.conn.commit()

    def create_card(self, number, pin, balance):
        self.cur.execute("INSERT INTO card (number, pin, balance) VALUES (?, ?, ?); ", (number, pin, balance))
        self.conn.commit()

    def delete_card(self, card):
        self.cur.execute("DELETE FROM card WHERE number=?", (card,))
        self.conn.commit()

    def transfer(self, card):
        print('\nTransfer\nEnter card number:')
        to_card = input()
        if to_card == card:
            print("You can't transfer money to the same account!\n")
        elif len(to_card) == 16 and self.luhn_alg(to_card):
            if self.read_card(to_card):
                print('Enter how much money you want to transfer:')
                transfer_amt = int(input())
                if self.read_card(card)[2] >= transfer_amt:
                    self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (transfer_amt, to_card))
                    self.cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?;", (transfer_amt, card))
                    self.conn.commit()
                    print('Success!\n')
                else:
                    print('Not enough money!\n')
            else:
                print('Such a card does not exist.\n')
        else:
            print('Probably you made mistake in the card number.\n')

    def read_card(self, card, *args):
        if args:
            query = """SELECT number, pin, balance FROM card WHERE number = ? AND pin = ?"""
            data_tuple = (card, args[0])
        else:
            query = """SELECT number, pin, balance FROM card WHERE number = ?"""
            data_tuple = (card,)
        self.cur.execute(query, data_tuple)
        rows = self.cur.fetchone()
        return rows

    def add_income(self, income, card):
        self.cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?;", (income, card))
        self.conn.commit()

    def menu(self):
        while not self.logged_in:
            print('1. Create an account\n2. Log into account\n0. Exit')
            choice = input()
            if choice == '1':
                self.create()
            elif choice == '2':
                self.login()
            elif choice == '0':
                print('\nBye!')
                self.cur.close()
                self.conn.close()
                quit()

    def account_menu(self, card, pin):
        while self.logged_in:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = input()
            if choice == '1':
                balance = self.read_card(card, pin)[2]
                print(f'\nBalance: {balance}\n')
            elif choice == '2':
                print('\nEnter income:')
                income = int(input())
                self.add_income(income, card)
                print()
            elif choice == '3':
                self.transfer(card)
            elif choice == '4':
                print('The account has been closed!')
                self.logged_in = False
                self.delete_card(card)
            elif choice == '5':
                self.logged_in = False
                print('\nYou have successfully logged out!\n')
            elif choice == '0':
                print('\nBye!')
                self.cur.close()
                self.conn.close()
                quit()

    def create(self):
        print()
        card = self.luhn_alg()
        pin = str.zfill(str(randint(0000, 9999)), 4)
        self.create_card(card, pin, 0)
        print(f'Your card has been created\nYour card number:\n{card}\nYour card PIN:\n{pin}\n')

    def login(self):
        print('\nEnter your card number:')
        card = input()
        print('Enter your PIN:')
        pin = input()
        cards = self.read_card(card, pin)
        if cards:
            print('\nYou have successfully logged in!\n')
            self.logged_in = True
            self.account_menu(card, pin)
        else:
            print('\nWrong card number or PIN!\n')

    def luhn_alg(self, *args):
        if not args:
            card = '400000' + str.zfill(str(randint(000000000, 999999999)), 9)
            card_check = [int(i) for i in card]
        else:
            card, check_sum = args[0], int(args[0][-1])
            card_check = [int(i) for i in card[:-1]]
        for index, _ in enumerate(card_check):
            if index % 2 == 0:
                card_check[index] *= 2
            if card_check[index] > 9:
                card_check[index] -= 9
        if not args:
            check_sum = str((10 - sum(card_check) % 10) % 10)
            card += check_sum
            return card
        if (sum(card_check) + check_sum) % 10 == 0:
            return True
        return False


if __name__ == '__main__':
    stage_4 = Bank()
