import socket
import chatlib
import random
import select

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
messages_to_send = []

ERROR_MSG = "Error!"
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


def recv_msg(conn):
    cmd = conn.recv(17).decode()
    if cmd == '':
        return ''
    len = conn.recv(4).decode()
    data = conn.recv(int(len) + 1).decode()
    return cmd + len + data


def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """
    global messages_to_send
    print(code, msg)
    data = chatlib.build_message(code, msg)
    print(data)
    if data is not None:
        print(f"saving msg: {(data, conn.getpeername())}")
        messages_to_send.append((conn, data))


def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    data = recv_msg(conn)
    print(f"received msg: {data}")
    cmd, msg = chatlib.parse_message(data)
    return cmd, msg


def print_client_sockets():
    for user in logged_users:
        print(logged_users[user])


# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {}
    for line in open("questions.txt", 'r'):
        details = line.split('|')
        questions[len(questions)] = {"question": details[0], "answers": details[1:-1], "correct": details[-1].split('\n')[0]}
    print(questions)
    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {}
    for line in open("users.txt", 'r'):
        details = line.split('|')
        users[details[0]] = {"password": details[1], "score": int(details[2]), "questions_asked": [int(id) if id != '' else None for id in details[-1].split('\n')[0].split(',')]}
    return users


def create_random_question(user):
    global questions
    global users
    non_answered = []
    for id in questions:
        if id not in users[user]["questions_asked"]:
            non_answered.append(id)
    if len(non_answered) == 0:
        return None
    chosen = random.choice(non_answered)
    return f'{chosen}|{questions[chosen]["question"]}|{"|".join(questions[chosen]["answers"])}|{questions[chosen]["correct"]}'


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    sock = socket.socket()
    sock.bind((SERVER_IP, SERVER_PORT))
    sock.listen()
    return sock


##### MESSAGE HANDLING


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users	 # To be used later
    username, password = data.split('|')
    if username in users and password == users[username]["password"]:
        build_and_send_message(conn, "LOGIN_OK", "")
        logged_users[conn.getpeername()] = username
    else:
        send_error(conn, "incorrect username or password")


def handle_getscore_message(conn, username):
    global users
    build_and_send_message(conn, "YOUR_SCORE", str(users[username]["score"]))


def handle_question_massage(conn, username):
    global users
    question_data = create_random_question(username)
    if question_data is None:
        build_and_send_message(conn, "NO_QUESTIONS", "")
    else:
        build_and_send_message(conn, "YOUR_QUESTION", question_data)
        users[username]["questions_asked"].append(int(question_data.split('|')[0]))


def handle_answer_massage(conn, username, answer):
    global users
    global questions
    q_id, ans_chosen = answer.split('|')
    if ans_chosen == questions[int(q_id)]["correct"]:
        users[username]["score"] += 1
        build_and_send_message(conn, "CORRECT_ANSWER", "")
    else:
        build_and_send_message(conn, "WRONG_ANSWER", questions[int(q_id)]["correct"])


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    del logged_users[conn.getpeername()]
    conn.close()


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users	 # To be used later
    if (cmd, data) == ("", ""):
        handle_logout_message(conn)
    if conn.getpeername() not in logged_users:
        if cmd == "LOGIN":
            handle_login_message(conn, data)
        else:
            send_error(conn, "must login before performing any other operations")
            return False
    else:
        if cmd == "MY_SCORE":
            handle_getscore_message(conn, logged_users[conn.getpeername()])
        elif cmd == "GET_QUESTION":
            handle_question_massage(conn, logged_users[conn.getpeername()])
        elif cmd == "SEND_ANSWER":
            handle_answer_massage(conn, logged_users[conn.getpeername()], data)
        elif cmd == "LOGOUT":
            handle_logout_message(conn)
        else:
            send_error(conn, "invalid command")
            print("sending error massage")
    return True


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, ERROR_MSG, error_msg)


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    global messages_to_send
    print("Welcome to Trivia Server!")
    users = load_user_database()
    questions = load_questions()
    server_socket = setup_socket()
    inputs = [server_socket]
    outputs = []
    while True:
        # Use select.select() to wait for input on the sockets
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        # Handle input on the readable sockets
        for socket in readable:
            if socket is server_socket:
                # If the readable socket is the server socket, accept a new connection
                client_socket, client_address = server_socket.accept()
                print(f'New connection from {client_address}')
                inputs.append(client_socket)
            else:
                # If the readable socket is a client socket, receive data from it
                cmd, data = recv_message_and_parse(socket)
                outputs.append(socket)
                if handle_client_message(socket, cmd, data) and (cmd == "LOGOUT" or (cmd, data) == ("", "")):
                    inputs.remove(socket)
                    outputs.remove(socket)

        # Handle output on the writable sockets
        for socket in writable:
            # If the writable socket is a client socket, send data to it and remove it from the output list
            response = f'Response from server to {socket.getpeername()}\n'
            for msg in messages_to_send:
                if msg[0] == socket:
                    socket.send(msg[1].encode())
                    messages_to_send.remove(msg)
            outputs.remove(socket)

        # Handle errors on the exceptional sockets
        for socket in exceptional:
            # If there is an error on a socket, remove it from the input and output lists and close it
            print(f'Exceptional condition on {socket.getpeername()}')
            inputs.remove(socket)
            outputs.remove(socket)
            handle_logout_message(socket)
    # while True:
    #     readable,
    #     print("waiting for client to connect")
    #     client_socket, client_addr = sock.accept()
    #     print("new client connected")
    #     command, data = recv_message_and_parse(client_socket)
    #     print(f'command: {command}, data: {data}')
    #     while handle_client_message(client_socket, command, data) and command != "LOGOUT":
    #         command, data = recv_message_and_parse(client_socket)


if __name__ == '__main__':
    main()