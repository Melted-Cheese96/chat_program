import socket
from time import sleep
import sys


# TO DO 11/1/19
# Continue code cleanup and organize all user options in self.main into functions for re-usability.
# Add the ability to clear notifications

class Client:
    def __init__(self):
        self.host = '127.0.0.1'
        self.user_options = {'0': self.check_notifications,
                             '1': self.send_message_to_another_user,
                             '2': self.check_messages,
                             '3': self.add_friend,
                             '4': self.send_remove_friend_request,
                             '5': self.check_friends_list,
                             '6': self.check_pending_friend_requests,
                             '7': self.accept_friend_request,
                             '8': self.retrieve_outgoing_friend_requests,
                             '9': self.clear_notifications,
                             }
        self.port = 9000
        self.account_options()

    def send_account_details(self, username, password):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((self.host, self.port))
            create_account_query = 'CRTACC'
            server.sendall(str.encode(create_account_query))
            sleep(1)
            server.sendall(str.encode(username))
            sleep(1)
            server.sendall(str.encode(password))
            while True:
                server_response = server.recv(1024)
                # print(server_response)
                if server_response:
                    result = server_response.decode()
                    break
            if result == 'Account has been made!':
                print(result)
                self.account_options()
        except:
            print('Connection error, make sure the server is up and you are connected to the internet!')
            self.account_options()

    def verify_account_details(self, username, password):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.connect((self.host, self.port))
            sign_in_query = 'SIGNIN'
            server_socket.sendall(str.encode(sign_in_query))
            sleep(1)
            server_socket.sendall(str.encode(username))
            sleep(1)
            server_socket.sendall(str.encode(password))
            while True:
                server_response = server_socket.recv(1024)
                if server_response:
                    verification_result = server_response.decode()
                    break
            print(verification_result)
            if verification_result == 'Password Confirmed!':
                self.main(username)
            elif verification_result == 'Credential Error!':
                self.account_options()
        except:
            print('Connection error, make sure the server is up and you are connected to the internet!')
            self.account_options()

    def quit_program(self):
        sys.exit()

    def account_options(self):
        print('Type in 1 to create a new account! \n')
        print('Type in 2 to sign into an existing account! \n')
        print('Type in 3 to exit program!')
        user_choice = input()
        if user_choice == '1':
            username = input('Username: ')
            if len(username) < 4 or len(username) > 12:
                print('Your username cannot be less than 4 characters and cannot be longer than 12 characters!')
                self.create_account()
            else:
                username = username.replace(' ', '')
                print('If your password has spaces they will be removed! \n')
                password = input('Password: ')
                password = password.replace(' ', '')
                self.send_account_details(username, password)
        elif user_choice == '2':
            username = input('Username: ')
            password = input('Password: ')
            self.verify_account_details(username, password)
        elif user_choice == '3':
            print('Quitting...')
            self.quit_program()
        else:
            print('Invalid command! Restarting...')
            self.account_options()

    def get_chat_history(self, username, chat_log_to_check):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        get_chat_history_query = 'GETCHATHISTORY'
        server.sendall(str.encode(get_chat_history_query))
        sleep(1)
        server.sendall(str.encode(username))
        sleep(1)
        server.sendall(str.encode(chat_log_to_check))
        while True:
            chat_history = server.recv(1024)
            if chat_history:
                print(chat_history.decode())
                break
        server.close()
        self.main(username)

    def add_friend(self, username):
        friend_username = input("Friend's username: ")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        add_friend_query = 'ADDFRIEND'
        try:
            server.connect((self.host, self.port))
            server.sendall(str.encode(add_friend_query))
            sleep(1)
            server.sendall(str.encode(username))
            sleep(1)
            server.sendall(str.encode(friend_username))
            while True:
                server_response = server.recv(1024)
                if server_response:
                    response = server_response.decode()
                    break
            print(response)
            server.close()
            self.main(username)
        except ConnectionRefusedError:
            print('Check the server status. Make sure you are connected to the internet!')

    def send_message_to_another_user(self, username):
        friend_username = input("Friend's username: ")
        msg = input('Message: ')
        send_message_query = 'SENDMESSAGE'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.connect((self.host, self.port))
            server.sendall(str.encode(send_message_query))
            sleep(1)
            server.sendall(str.encode(username))
            sleep(1)
            server.sendall(str.encode(friend_username))
            sleep(1)
            server.sendall(str.encode(msg))
            while True:
                server_response = server.recv(1024)
                if server_response:
                    result = server_response.decode()
                    break
            print(result)
            server.close()
            self.main(username)
        except ConnectionRefusedError:
            print('Make sure the server is up, check your internet connection!')
            self.main(username)

    def check_messages(self, username):
        list_of_items = []
        get_chat_log_query = 'GETCHATLIST'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(get_chat_log_query))
        sleep(1)
        server.sendall(str.encode(username))
        while True:
            chat_log_names = server.recv(1024)
            if chat_log_names:
                if chat_log_names.decode() == 'FINISH':
                    break
                else:
                    print(chat_log_names.decode())
                    list_of_items.append(chat_log_names.decode())
        if list_of_items[0] == 'You have no chat logs!':
            self.main(username)
        else:
            for name in list_of_items:
                name = name.split(' ')
                print(name[0])
            chat_log_to_check = input('Enter chat log name: ')
            server.close()
            self.get_chat_history(username, chat_log_to_check)

    def check_notifications(self, username):
        notifications_request = 'GETNOTIFICATIONS'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(notifications_request))
        sleep(1)
        server.sendall(str.encode(username))
        while True:
            response = server.recv(1024)
            if response:
                result = response.decode()
                break
        print(result)
        print('\n')
        server.close()
        self.main(username)

    def check_pending_friend_requests(self, username):
        check_pending_requests_username = 'VIEWREQUESTS'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(check_pending_requests_username))
        sleep(1)
        server.sendall(str.encode(username))
        while True:
            server_response = server.recv(1024)
            if server_response:
                result = server_response.decode()
                break
        print(result)
        server.close()
        self.main(username)

    def check_friends_list(self, username):
        check_friends_list_query = 'GETFRIENDS'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(check_friends_list_query))
        sleep(1)
        server.sendall(str.encode(username))
        while True:
            server_response = server.recv(1024)
            if server_response:
                result = server_response.decode()
                break
        print(result)
        server.close()
        self.main(username)

    def accept_friend_request(self, username):
        accept_friend_request_query = 'ACCEPTREQUEST'
        user_to_accept = input("Friend's username: ")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(accept_friend_request_query))
        sleep(1)
        server.sendall(str.encode(username))
        sleep(1)
        server.sendall(str.encode(user_to_accept))
        while True:
            server_response = server.recv(1024)
            if server_response:
                response = server_response.decode()
                break
        print(response)
        server.close()
        self.main(username)

    def clear_notifications(self, username):
        clear_notifications_request = 'CLEAR'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(clear_notifications_request))
        sleep(1)
        server.sendall(str.encode(username))
        while True:
            server_response = server.recv(1024)
            if server_response:
                response = server_response.decode()
                break
        print(response)
        server.close()
        self.main(username)

    def send_remove_friend_request(self, username):
        user_to_unfriend = input('Enter user to unfriend: ')
        remove_friend_query = 'REMOVEFRIEND'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(remove_friend_query))
        sleep(1)
        server.sendall(str.encode(username))
        sleep(1)
        server.sendall(str.encode(user_to_unfriend))
        while True:
            server_response = server.recv(1024)
            if server_response:
                result = server_response.decode()
                break
        print(result)
        server.close()
        self.main(username)

    def retrieve_outgoing_friend_requests(self, username):
        view_outgoing_friend_requests_query = 'VIEWOUTGOING'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((self.host, self.port))
        server.sendall(str.encode(view_outgoing_friend_requests_query))
        sleep(1)
        server.sendall(str.encode(username))
        while True:
            server_response = server.recv(1024)
            if server_response:
                result = server_response.decode()
                break
        print(result)
        server.close()
        self.main(username)

    def main(self, username):
        print('Type in 0 to check your notifications')
        print('Type in 1 to send a message to another user!')
        print('Type in 2 to check your messages!')
        print('Type in 3 to send a friend request!')
        print('Type in 4 to remove a friend!')
        print('Type in 5 to check your friends list!')
        print('Type in 6 to check your pending friend requests!')
        print('Type in 7 to accept a friend request!')
        print('Type in 8 to check your outgoing friend requests!')
        print('Type in 9 to clear your notifications!')
        print('Type in 10 to log out!')
        print('Type in 11 to exit program')
        user_choice = input()
        if user_choice == '10':
            self.account_options()
        elif user_choice == '11':
            sys.exit()
        elif user_choice in self.user_options:
            func = self.user_options.get(user_choice)
            func(username)
        else:
            print('Invalid input!')
            self.main(username)


c = Client()
