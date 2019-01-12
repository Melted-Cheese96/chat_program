import socket
import threading
from time import sleep
import os
from passlib.hash import pbkdf2_sha256
import pickle

# Let the user know when they have unread DM's
# Add ability to delete account.
# Up to date version as of 12/1/19
# Refactor large if/elif chain and organize into a dict.

class ChatServer:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 9000
        self.starting_dir = os.getcwd()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.user_directory = {}
        self.ports_taken = []
        self.chat_logs = []
        self.check_for_user_directory()
        self.listen()

    def check_for_user_directory(self):
        if '.users' in os.listdir():
            pass
        else:
            os.mkdir('.users')

    def listen(self):
        self.server.listen(5)
        while True:
            print(self.ports_taken)
            print('Server running!')
            c, addr = self.server.accept()
            print('Connection from {}'.format(addr))
            self.handle_client(c)
            # handle_information_thread = threading.Thread(target=self.handle_client(c))
            # handle_information_thread.start()

    def create_new_account(self, username, password, client):
        os.chdir('.users')
        if username in os.listdir():
            client.sendall(b'Username already taken!')
        else:
            username = '.' + username
            os.mkdir(username)
            hashed_password = pbkdf2_sha256.hash(password)
            os.chdir(username)
            with open('.info', 'wb') as doc:
                pickle.dump(hashed_password, doc)
            os.mkdir('.messages')
            os.mkdir('.outgoing requests')
            os.mkdir('.incoming requests')
            with open('.notifications', 'x') as doc:
                pass
            with open('.friends', 'x') as doc:
                pass
            self.notify_user(username, 'You have made an account!')
            client.sendall(b'Account has been made!')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

    def verify_account_details(self, username, password, client):
        os.chdir('.users')
        username = '.' + username
        print(username)
        print(os.listdir())
        if username in os.listdir():
            print('Account was found!')
            os.chdir(username)
            with open('.info', 'rb') as doc:
                hashed_p = pickle.load(doc)
            verification = pbkdf2_sha256.verify(password, hashed_p)
            print(verification)
            if verification is True:
                client.sendall(b'Password Confirmed!')
            elif verification is False:
                client.sendall(b'Credential Error!')
            os.chdir(self.starting_dir)
            client.close()
            self.listen()
        else:
            print('Account not found!')
            client.sendall(b'Account not found!')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

    def send_message(self, to_user, from_user, message, client):
        '''This function is responsible for sending messages
        from one user to another. to_user is the recipient for the message,
        from_user is the sender of the message.'''
        message = '{}: {}'.format(from_user, message)
        to_user = '.' + to_user
        from_user = '.' + from_user
        os.chdir('.users')
        if to_user in os.listdir():
            '''
            This runs when to_user was found in the .users folder.
            The message sent by from_user is stored in a log in both their folders.
            '''
            os.chdir(to_user)
            os.chdir('.messages')
            file_name = '{} DM LOG'.format(from_user)
            if file_name in os.listdir():
                with open(file_name, 'r') as doc:
                    chat_logs = doc.read()
                with open(file_name, 'w') as doc:
                    doc.write(chat_logs)
                    doc.write('\n')
                    doc.write(message)
            else:
                with open(file_name, 'w') as doc:
                    doc.write(message)
            os.chdir(self.starting_dir)
            os.chdir('.users')
            os.chdir(from_user)
            os.chdir('.messages')
            new_file_name = '{} DM LOG'.format(to_user)
            if new_file_name in os.listdir():
                with open(new_file_name, 'r') as doc:
                    file_content = doc.read()
                with open(new_file_name, 'w') as doc:
                    doc.write(file_content)
                    doc.write('\n')
                    doc.write(message)
            else:
                with open(new_file_name, 'w') as doc:
                    doc.write(message)
            client.sendall(b'Message has been sent!')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

        else:
            print('User was not found!')
            client.sendall(b'User not found!')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

    def get_dm_list(self, username, client):
        username = '.' + username
        try:
            os.chdir('.users')
            os.chdir(username)
            os.chdir('.messages')
            chat_log_items = os.listdir()
            if len(chat_log_items) == 0:
                client.sendall(b'You have no chat logs!')
                sleep(1)
                client.sendall(b'FINISH')
                client.close()
                os.chdir(self.starting_dir)
                self.listen()
            else:
                for item in os.listdir():
                    print(item)
                    client.sendall(str.encode(item))
                    sleep(1)
                sleep(1)
                client.sendall(b'FINISH')
                client.close()
                os.chdir(self.starting_dir)
                self.listen()
        except FileNotFoundError:
            print('One of the files was not found!')
            client.sendall(b'Error.')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

    def get_chat_history(self, username, chat_log, client):
        try:
            os.chdir('.users')
            os.chdir(username)
            os.chdir('.messages')
            chat_log = '.' + chat_log
            found = 0
            for item in os.listdir():
                if chat_log in item:
                    found += 1
                    with open(item, 'r') as doc:
                        file_content = doc.read()
            if found == 0:
                client.sendall(b'User not found')
                client.close()
                os.chdir(self.starting_dir)
                self.listen()
            else:
                print(file_content)
                client.sendall(str.encode(file_content))
                client.close()
                os.chdir(self.starting_dir)
                self.listen()
        except FileNotFoundError:
            client.sendall(b'Error.')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

    def send_friend_request(self, username, friend_username, client_obj):
        '''
        Sends a friend request from user1 to user2.
        '''

        username = '.' + username
        friend_username = '.' + friend_username
        os.chdir('.users')
        if username in os.listdir():
            user_dir = os.getcwd()
            os.chdir(username)
            with open('.friends', 'r') as doc:
                content = doc.read()
            if friend_username in content:
                client_obj.sendall(b'That user is already your friend!')
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
            else:
                os.chdir(user_dir)
                if friend_username in os.listdir():
                    os.chdir(username)
                    os.chdir('.outgoing requests')
                    incoming_requests_file_name = friend_username
                    with open(incoming_requests_file_name, 'w') as doc:
                        doc.write('Pending')
                    os.chdir(user_dir)
                    os.chdir(friend_username)
                    os.chdir('.incoming requests')
                    file_name = username
                    with open(file_name, 'w') as doc:
                        doc.write('Not Accepted')
                    os.chdir(self.starting_dir)
                    response = 'Friend request sent to {}'.format(friend_username)
                    client_obj.sendall(str.encode(response))
                    client_obj.close()
                    self.notify_user(username, "Friend request sent to {}".format(friend_username))
                    self.notify_user(friend_username, "{} has sent you a friend request!".format(username))
                    self.listen()
        else:
            client_obj.sendall(b'The user that you entered was not found!')

    def get_friends_list(self, client_username, client_obj):
        client_username = '.' + client_username
        os.chdir('.users')
        os.chdir(client_username)
        with open('.friends', 'r') as doc:
            content = doc.read()
        if len(content) == 0:
            client_obj.sendall(b'No friends...')
            client_obj.close()
            os.chdir(self.starting_dir)
            self.listen()
        else:
            client_obj.sendall(str.encode(content))
            os.chdir(self.starting_dir)
            client_obj.close()
            self.listen()

    def view_incoming_requests(self, username, client_obj):
        username = '.' + username
        os.chdir('.users')
        if username in os.listdir():
            os.chdir(username)
            os.chdir('.incoming requests')
            items = os.listdir()
            if len(items) == 0:
                client_obj.sendall(b'You have no incoming friend requests!')
                sleep(1)
                client_obj.sendall(b'FINISH')
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
            else:
                for item in os.listdir():
                    info = 'Friend request from {}'.format(item)
                    client_obj.sendall(str.encode(info))
                    sleep(1)
                sleep(1)
                client_obj.sendall(b'FINISH')
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
        else:
            client_obj.sendall(b'Your username was not found! Make sure that your username is valid.')

    def view_outgoing_requests(self, username, client_obj):
        os.chdir('.users')
        username = '.' + username
        if username in os.listdir():
            os.chdir(username)
            os.chdir('.outgoing requests')
            items = os.listdir()
            if len(items) == 0:
                client_obj.sendall(b'You have no outgoing requests!')
                sleep(1)
                client_obj.sendall(b'FINISH')
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
            else:
                for item in os.listdir():
                    info = 'Friend request to {}'.format(item)
                    client_obj.sendall(str.encode(info))
                    sleep(1)
                sleep(1)
                client_obj.sendall(b'FINISH')
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
        else:
            client_obj.sendall(b'Your username was not found! Make sure that your username is valid.')
            client_obj.close()
            os.chdir(self.starting_dir)
            self.listen()

    def accept_friend_request(self, username, user_to_accept, client_obj):
        username = '.' + username
        user_to_accept = '.' + user_to_accept
        os.chdir('.users')
        os.chdir(username)
        user_direc = os.getcwd()
        os.chdir('.incoming requests')
        if user_to_accept in os.listdir():
            os.remove(user_to_accept)
            os.chdir(user_direc)
            with open('.friends', 'r') as doc:
                content = doc.read()
            with open('.friends', 'w') as doc:
                doc.write(content)
                doc.write('\n')
                doc.write(user_to_accept)
            os.chdir(self.starting_dir)
            os.chdir('.users')
            os.chdir(user_to_accept)
            user_direc = os.getcwd()
            os.chdir('.outgoing requests')
            os.remove(username)
            os.chdir(user_direc)
            with open('.friends', 'r') as doc:
                content = doc.read()
            with open('.friends', 'w') as doc:
                doc.write(content)
                doc.write('\n')
                doc.write(username)
            os.chdir(self.starting_dir)
            information_to_send_back = '{} is now your friend'.format(user_to_accept)
            client_obj.sendall(str.encode(information_to_send_back))
            client_obj.close()
            self.notify_user(user_to_accept, "{} has accepted your friend request!".format(username))
            self.notify_user(username, "{} is now your friend!".format(user_to_accept))
            self.listen()

        else:
            client_obj.sendall(b'User did not send you a friend request!')
            client_obj.close()
            os.chdir(self.starting_dir)
            self.listen()

    def unfriend_user(self, username, user_to_remove, client):  # Function responsible for unfriending.
        username = '.' + username
        user_to_remove = '.' + user_to_remove
        os.chdir('.users')
        main_user_dir = os.getcwd()
        if user_to_remove in os.listdir():
            os.chdir(username)
            with open('.friends', 'r') as doc:
                content = doc.read()
            if user_to_remove in content:
                print('User was found in friends list!')
                content = content.replace(user_to_remove, '')
                content = content.replace('\n', '')
                with open('.friends', 'w') as doc:
                    doc.write(content)
                os.chdir(main_user_dir)
                os.chdir(user_to_remove)
                with open('.friends', 'r') as doc:
                    content = doc.read()
                content = content.replace(username, '')
                content = content.replace('\n', '')
                with open('.friends', 'w') as doc:
                    doc.write(content)
                send_back_message = '{} has been unfriended'.format(user_to_remove)
                client.sendall(str.encode(send_back_message))
                client.close()
                os.chdir(self.starting_dir)
                self.notify_user(user_to_remove, "{} has removed you as a friend".format(username))
                self.notify_user(username, "You have removed {} as a friend".format(user_to_remove))
                self.listen()
            else:
                print('User was not found in friends list!')
                client.sendall(b'That user is not in your friends list!')
                client.close()
                os.chdir(self.starting_dir)
                self.listen()
        else:
            print('User not found!')
            client.sendall(b'That user was not found!')
            client.close()
            os.chdir(self.starting_dir)
            self.listen()

    def get_notifications(self, username, client_obj):
        username = '.' + username
        os.chdir('.users')
        if username in os.listdir():
            os.chdir(username)
            with open('.notifications', 'r') as doc:
                all_notifications = doc.read()
            if len(all_notifications) == 0:
                client_obj.sendall(b'You have no notifications!')
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
            else:
                client_obj.sendall(str.encode(all_notifications))
                client_obj.close()
                os.chdir(self.starting_dir)
                self.listen()
        else:
            client_obj.sendall(b'Error, username was not found in database!')
            client_obj.close()
            os.chdir(self.starting_dir)
            self.listen()

    def clear_notifications(self, username, client_obj):
        if '.' in username:
            pass
        else:
            username = '.' + username
        if os.getcwd() == self.starting_dir:
            pass
        else:
            os.chdir(self.starting_dir)
        os.chdir('.users')
        if username in os.listdir():
            os.chdir(username)
            os.remove('.notifications')
            with open('.notifications', 'x') as doc:
                pass
            client_obj.sendall(b'Your notifications have been cleared!')
            client_obj.close()
            os.chdir(self.starting_dir)
            self.listen()
        else:
            client_obj.sendall(b'Error, your username is not valid!')
            client_obj.close()
            os.chdir(self.starting_dir)
            self.listen()

    def notify_user(self, user_to_notify, message):
        print('Notifying {}...'.format(user_to_notify))
        if '.' in user_to_notify:
            pass
        else:
            user_to_notify = '.' + user_to_notify
        current_directory = os.getcwd()
        if current_directory == self.starting_dir:
            pass
        else:
            os.chdir(self.starting_dir)
        os.chdir('.users')
        if user_to_notify in os.listdir():
            os.chdir(user_to_notify)
            if '.notifications' in os.listdir():
                print('Notifications file found!')
                with open('.notifications', 'r') as doc:
                    current_notifications = doc.read()

                with open('.notifications', 'w') as doc:
                    doc.write(current_notifications)
                    doc.write('\n')
                    doc.write(message)
            else:
                with open('.notifications', 'w') as doc:
                    doc.write(message)

            print('{} has been notified!'.format(user_to_notify))
            os.chdir(self.starting_dir)

        else:
            print('User not found in .users directory')
            os.chdir(self.starting_dir)

    def handle_client(self, client):
        '''
        This function is run in a separate thread to the listening() function.
        This thread retrieves the user request, then listens for necessary information to complete the user's request,
        then does the necessary things to complete the user request and sends a response to the client.
        '''
        threading.Thread(target=self.listen).start()
        while True:
            user_choice = client.recv(1024)
            print(user_choice)
            if user_choice:
                if user_choice.decode() == 'SENDMESSAGE':  # If the user sends' SENDMESSAGE' then the server knows the user wants to send a message to another user!
                    print('User wants to send a message to another user!')
                    while True:
                        client_username = client.recv(1024) # Gets the username of the sender!
                        if client_username:
                            client_username = client_username.decode()
                            print(client_username)
                            while True:
                                to_user = client.recv(1024) # Gets the username of the recipient
                                if to_user:
                                    to_user = to_user.decode()
                                    print(to_user)
                                    while True:
                                        message_to_send = client.recv(1024)
                                        if message_to_send:
                                            message_to_send = message_to_send.decode()
                                            print(message_to_send)
                                            self.send_message(to_user, client_username, message_to_send, client)

                elif user_choice.decode() == 'CRTACC':
                    print('User wants to create account!')
                    while True:
                        new_username = client.recv(1024)
                        if new_username:
                            new_username = new_username.decode()
                            print(new_username)
                            while True:
                                new_password = client.recv(1024)
                                if new_password:
                                    new_password = new_password.decode()
                                    print(new_password)
                                    self.create_new_account(new_username, new_password, client)
                elif user_choice.decode() == 'SIGNIN':
                    print('User wants to sign into an existing account!')
                    while True:
                        username = client.recv(1024)
                        if username:
                            username = username.decode()
                            print(username)
                            while True:
                                password = client.recv(1024)
                                if password:
                                    password = password.decode()
                                    print(password)
                                    self.verify_account_details(username, password, client)
                elif user_choice.decode() == 'GETCHATLIST':
                    print('User wants to check chat log!')
                    while True:
                        username = client.recv(1024)
                        if username:
                            username = username.decode()
                            print(username)
                            self.get_dm_list(username, client)
                elif user_choice.decode() == 'GETCHATHISTORY':
                    print('User wants to check their chat history!')
                    while True:
                        username = client.recv(1024)
                        if username:
                            username = username.decode()
                            username = '.' + username
                            while True:
                                chat_log_to_check = client.recv(1024)  # This should get a username of the chat log the user is wanting to check.
                                if chat_log_to_check:
                                    chat_log_to_check = chat_log_to_check.decode()
                                    print(chat_log_to_check)
                                    self.get_chat_history(username, chat_log_to_check, client)

                elif user_choice.decode() == 'ADDFRIEND':  # Sends friend request to the other user!
                    print('User wants to add a new friend!')
                    while True:
                        client_username = client.recv(1024)
                        if client_username:
                            client_username = client_username.decode()
                            print(client_username)
                            while True:
                                friend_username = client.recv(1024)
                                if friend_username:
                                    friend_username = friend_username.decode()
                                    print(friend_username)
                                    self.send_friend_request(client_username, friend_username, client)

                elif user_choice.decode() == 'REMOVEFRIEND':  # Removes friend from users friend file
                    while True:
                        username = client.recv(1024)
                        if username:
                            username = username.decode()
                            # print(username)
                            while True:
                                user_to_remove = client.recv(1024)
                                if user_to_remove:
                                    user_to_remove = user_to_remove.decode()
                                    # print(user_to_remove)
                                    self.unfriend_user(username, user_to_remove, client)

                elif user_choice.decode() == 'GETFRIENDS':  # Retrieves friend list from user and returns it to them.
                    print('User wants to get their friends list!')
                    while True:
                        client_username = client.recv(1024)
                        if client_username:
                            client_username = client_username.decode()
                            print(client_username)
                            self.get_friends_list(client_username, client)

                elif user_choice.decode() == 'ACCEPTREQUEST':  # Allows the user to accept a friend request.
                    print('User wants to accept a friend request!')
                    while True:
                        client_username = client.recv(1024)
                        if client_username:
                            client_username = client_username.decode()
                            print(client_username)
                            while True:
                                user_to_accept = client.recv(1024)
                                if user_to_accept:
                                    user_to_accept = user_to_accept.decode()
                                    print(user_to_accept)
                                    self.accept_friend_request(client_username, user_to_accept, client)

                elif user_choice.decode() == 'VIEWREQUESTS':  # Lets the user review their current friend requests.
                    print('User wants to see their pending friend requests!')
                    while True:
                        username = client.recv(1024)
                        if username:
                            username = username.decode()
                            print(username)
                            self.view_incoming_requests(username, client)

                elif user_choice.decode() == 'VIEWOUTGOING':
                    print('User wants to see their outgoing friend requests!')
                    username = client.recv(1024)
                    if username:
                        username = username.decode()
                        self.view_outgoing_requests(username, client)

                elif user_choice.decode() == 'GETNOTIFICATIONS':
                    while True:
                        username = client.recv(1024)
                        if username:
                            username = username.decode()
                            self.get_notifications(username, client)

                elif user_choice.decode() == 'CLEAR':
                    username = client.recv(1024)
                    if username:
                        username = username.decode()
                        print(username)
                        self.clear_notifications(username, client)


server = ChatServer()
