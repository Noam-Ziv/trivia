import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****


SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


# HELPER SOCKET METHODS

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


def connect():
    sock = socket.socket()
    sock.connect((SERVER_IP, SERVER_PORT))
    return sock


def error_and_exit(msg):
    print(msg)
    exit()


def login(conn):
    username = input("Please enter username: \n")
    password = input("Please enter password: \n")
    build_and_send_message(conn, "LOGIN", f'{username}|{password}')
    response = recv_message_and_parse(conn)
    while response == (None, None) or response[0] != "LOGIN_OK":
        print("login failed")
        build_and_send_message(conn, "LOGIN", f'{username}|{password}')
        response = recv_message_and_parse(conn)
    print("login succeeded")


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
    conn.close()


def main():
    sock = connect()
    login(sock)
    logout()

if __name__ == "__main__":
    main()


