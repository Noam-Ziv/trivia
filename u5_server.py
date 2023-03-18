import socket
import chatlib

# GLOBALS
users = {}
questions = {}
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later

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
    print(code, msg)
    data = chatlib.build_message(code, msg)
    print(data)
    if data is not None:
        print(f"sending msg: {data}")
        conn.send(data.encode())


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


# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {
        "test":	{"password": "test", "score": 0, "questions_asked": []},
        "yossi": {"password": "123", "score": 50, "questions_asked": []},
        "master": {"password": "master", "score": 200, "questions_asked": []}
    }
    return users


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


def send_error(conn, error_msg):
    """
    Send error message with given message
    Recieves: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, ERROR_MSG, error_msg)


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
        logged_users[conn.getsockname()] = username
    else:
        send_error(conn, "incorrect username or password")


def handle_getscore_message(conn, username):
    global users


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users
    conn.close()


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Recieves: socket, message code and data
    Returns: None
    """
    global logged_users	 # To be used later
    if cmd == "LOGIN":
        handle_login_message(conn, data)
    else:
        print("sending error massage")
        send_error(conn, "invalid command")


def main():
    # Initializes global users and questions dicionaries using load functions, will be used later
    global users
    global questions
    print("Welcome to Trivia Server!")
    users = load_user_database()
    questions = load_questions()
    sock = setup_socket()
    while True:
        client_socket, client_addr = sock.accept()
        print("new client connected")
        command, data = recv_message_and_parse(client_socket)
        print(f'command: {command}, data: {data}')
        while command != "LOGOUT":
            handle_client_message(client_socket, command, data)
            command, data = recv_message_and_parse(client_socket)
        handle_logout_message()


if __name__ == '__main__':
    main()