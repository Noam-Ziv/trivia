import chatlib
import socket

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


def connect():
    sock = socket.socket()
    sock.connect((SERVER_IP, SERVER_PORT))
    return sock


def recv_msg(conn):
    part_of_msg = conn.recv(1).decode()
    full_msg = part_of_msg
    while len(part_of_msg) == 1:
        part_of_msg = conn.recv(1).decode()
        full_msg += part_of_msg
    return full_msg


def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """
    data = chatlib.build_message(code, msg)
    if data is None:
        print(f"an error occurred, could not send massage")
    else:
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
    while response == (None, None) or response[0] != "LOGIN_OK":
        print("login failed")
        response = build_send_recv_parse(conn, "LOGIN", f'{username}|{password}')
    print("login succeeded")


def get_score(conn):
    response = build_send_recv_parse(conn, "MY_SCORE", "")
    if response == (None, None) or response[0] != "YOUR_SCORE":
        print("an error occurred")
    else:
        print(f"your score is: {response[1]}")


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
    conn.close()


def error_and_exit(msg):
    print(msg)
    exit()


def main():
    sock = connect()
    login(sock)
    cmd = input("what would you like to do?\n")
    while cmd != "logout":
        if cmd == "MY_SCORE":
            get_score(sock)
        else:
            print("invalid command")
        cmd = input("what would you like to do?\n")
    logout()

if __name__ == "__main__":
    main()





