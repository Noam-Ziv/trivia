import chatlib
import socket

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


def connect():
    sock = socket.socket()
    sock.connect((SERVER_IP, SERVER_PORT))
    print("connected to server")
    return sock


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
    data = chatlib.build_message(code, msg)
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


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    return recv_message_and_parse(conn)


def login(conn):
    username = input("Please enter username: \n")
    password = input("Please enter password: \n")
    response = build_send_recv_parse(conn, "LOGIN", f'{username}|{password}')
    print(f'response: {response}')
    while response[0] != "LOGIN_OK":
        if response == (None, None):
            print("login failed")
        else:
            print(f"login failed, {response[1]}")
            username = input("Please enter username: \n")
            password = input("Please enter password: \n")
        response = build_send_recv_parse(conn, "LOGIN", f'{username}|{password}')
    print("login succeeded")


def get_score(conn):
    response = build_send_recv_parse(conn, "MY_SCORE", "")
    if response[0] == "YOUR_SCORE":
        print(f"your score is: {response[1]}")
    else:
        error_and_exit(response[1])


def play_question(conn):
    question_response = build_send_recv_parse(conn, "GET_QUESTION", "")
    if question_response[0] == "YOUR_QUESTION":
        question_data = question_response[1].split('|')
        q_id, question = question_data[:2]
        answers = question_data[2:]
        print(f'{question}\n1. {answers[0]}\n2. {answers[1]}\n3. {answers[2]}\n4. {answers[3]}\n')
        player_answer = int(input("enter the number of your answer: "))
        is_correct = build_send_recv_parse(conn, "SEND_ANSWER", f'{q_id}|{player_answer}')
        if is_correct[0] == "CORRECT_ANSWER":
            print("you are correct")
            print(f"correct answer is: {answers[player_answer - 1]}")
        elif is_correct[0] == "WRONG_ANSWER":
            print("you are wrong")
            print(f"correct answer is: {answers[int(is_correct[1]) - 1]}")
        else:
            error_and_exit(is_correct[1])
    elif question_response[0] == "NO_QUESTIONS":
        print("no more questions are available")
    else:
        error_and_exit(question_response[1])


def get_highscore(conn):
    highscore_response = build_send_recv_parse(conn, "HIGHSCORE", "")
    if highscore_response[0] == "ALL_SCORE":
        highscore_table = highscore_response[1].split('\n')
        for score in highscore_table:
            print(score)
    else:
        error_and_exit(highscore_response[1])


def get_logged_users(conn):
    logged_response = build_send_recv_parse(conn, "LOGGED", "")
    if logged_response[0] == "LOGGED_ANSWER":
        logged_users = logged_response[1]
        print(f'all the currently logged users are:\n{logged_users}')
    else:
        error_and_exit(logged_response[1])


def logout(conn):
    build_and_send_message(conn, "LOGOUT", "")
    conn.close()


def error_and_exit(msg):
    if msg is not None:
        print(msg)
    exit()


def main():
    sock = connect()
    login(sock)
    cmd = input("what would you like to do?\n")
    while cmd != "logout":
        if cmd == "get score":
            get_score(sock)
        elif cmd == "play question":
            play_question(sock)
        elif cmd == "get highscore":
            get_highscore(sock)
        elif cmd == "get logged users":
            get_logged_users(sock)
        else:
            print("invalid command")
        cmd = input("what would you like to do?\n")
    logout(sock)


if __name__ == "__main__":
    main()


