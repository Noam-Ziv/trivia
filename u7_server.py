# import socket
# import chatlib
# import random
#
# # GLOBALS
# users = {}
# questions = {}
# logged_users = {}  # a dictionary of client hostnames to usernames - will be used later
#
# ERROR_MSG = "Error!"
# SERVER_PORT = 5678
# SERVER_IP = "127.0.0.1"
#
#
# def recv_msg(conn):
#     cmd = conn.recv(17).decode()
#     if cmd == '':
#         return ''
#     len = conn.recv(4).decode()
#     data = conn.recv(int(len) + 1).decode()
#     return cmd + len + data
#
#
# def build_and_send_message(conn, code, msg):
#     """
#     Builds a new message using chatlib, wanted code and message.
#     Prints debug info, then sends it to the given socket.
#     Paramaters: conn (socket object), code (str), msg (str)
#     Returns: Nothing
#     """
#     print(code, msg)
#     data = chatlib.build_message(code, msg)
#     print(data)
#     if data is not None:
#         print(f"sending msg: {data}")
#         conn.send(data.encode())
#
#
# def recv_message_and_parse(conn):
#     """
#     Recieves a new message from given socket.
#     Prints debug info, then parses the message using chatlib.
#     Paramaters: conn (socket object)
#     Returns: cmd (str) and data (str) of the received message.
#     If error occured, will return None, None
#     """
#     data = recv_msg(conn)
#     print(f"received msg: {data}")
#     cmd, msg = chatlib.parse_message(data)
#     return cmd, msg
#
#
# # Data Loaders #
#
# def load_questions():
#     """
#     Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
#     Recieves: -
#     Returns: questions dictionary
#     """
#     questions = {}
#     for line in open("questions.txt", 'r'):
#         details = line.split('|')
#         questions[len(questions)] = {"question": details[0], "answers": details[1:-1], "correct": details[-1].split('\n')[0]}
#     return questions
#
#
# def load_user_database():
#     """
#     Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
#     Recieves: -
#     Returns: user dictionary
#     """
#     users = {}
#     for line in open("users.txt", 'r'):
#         details = line.split('|')
#         users[details[0]] = {"password": details[1], "score": int(details[2]), "questions_asked": [int('0' + id) for id in details[-1].split('\n')[0].split(',')]}
#     return users
#
#
# def create_random_question(user):
#     questions = load_questions()
#     users = load_user_database()
#     non_answered = []
#     for id in questions:
#         if id not in users[user]["questions_asked"]:
#             non_answered.append(id)
#     if len(non_answered) == 0:
#         return None
#     chosen = random.choice(non_answered)
#     return f'{chosen}|{questions[chosen]["question"]}|{"|".join(questions[chosen]["answers"])}|{questions[chosen]["correct"]}'
#
#
# # SOCKET CREATOR
#
# def setup_socket():
#     """
#     Creates new listening socket and returns it
#     Recieves: -
#     Returns: the socket object
#     """
#     sock = socket.socket()
#     sock.bind((SERVER_IP, SERVER_PORT))
#     sock.listen()
#     return sock
#
#
# ##### MESSAGE HANDLING
#
#
# def handle_login_message(conn, data):
#     """
#     Gets socket and message data of login message. Checks  user and pass exists and match.
#     If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
#     Recieves: socket, message code and data
#     Returns: None (sends answer to client)
#     """
#     global users  # This is needed to access the same users dictionary from all functions
#     global logged_users	 # To be used later
#     username, password = data.split('|')
#     if username in users and password == users[username]["password"]:
#         build_and_send_message(conn, "LOGIN_OK", "")
#         logged_users[conn.getsockname()] = username
#     else:
#         send_error(conn, "incorrect username or password")
#
#
# def handle_getscore_message(conn, username):
#     global users
#     build_and_send_message(conn, "YOUR_SCORE", str(users[username]["score"]))
#
#
# def handle_question_massage(conn, username):
#     question_data = create_random_question(username)
#     if question_data is None:
#         build_and_send_message(conn, "NO_QUESTIONS", "")
#     else:
#         build_and_send_message(conn, "YOUR_QUESTION", question_data)
#
#
# def handle_answer_massage(conn, username, answer):
#     global users
#     global questions
#     q_id, ans_chosen = answer.split('|')
#     if ans_chosen == questions[int(q_id)]["correct"]:
#         users[username]["score"] += 1
#         build_and_send_message(conn, "CORRECT_ANSWER", "")
#     else:
#         build_and_send_message(conn, "WRONG_ANSWER", questions[q_id]["correct"])
#
#
# def handle_logout_message(conn):
#     """
#     Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
#     Recieves: socket
#     Returns: None
#     """
#     global logged_users
#     del logged_users[conn.getsockname()]
#     conn.close()
#
#
# def handle_client_message(conn, cmd, data):
#     """
#     Gets message code and data and calls the right function to handle command
#     Recieves: socket, message code and data
#     Returns: None
#     """
#     global logged_users	 # To be used later
#     if conn.getsockname() not in logged_users:
#         if cmd == "LOGIN":
#             handle_login_message(conn, data)
#         else:
#             send_error(conn, "must login before performing any other operations")
#     else:
#         if cmd == "MY_SCORE":
#             handle_getscore_message(conn, logged_users[conn.getsockname()])
#         elif cmd == "GET_QUESTION":
#             handle_question_massage(conn, logged_users[conn.getsockname()])
#         elif cmd == "SEND_ANSWER":
#             handle_answer_massage(conn, logged_users[conn.getsockname()], data)
#         elif cmd == "LOGOUT":
#             handle_logout_message(conn)
#         else:
#             send_error(conn, "invalid command")
#             print("sending error massage")
#     return True
#
#
# def send_error(conn, error_msg):
#     """
#     Send error message with given message
#     Recieves: socket, message error string from called function
#     Returns: None
#     """
#     build_and_send_message(conn, ERROR_MSG, error_msg)
#
#
# def main():
#     # Initializes global users and questions dicionaries using load functions, will be used later
#     global users
#     global questions
#     print("Welcome to Trivia Server!")
#     users = load_user_database()
#     questions = load_questions()
#     sock = setup_socket()
#     while True:
#         print("waiting for client to connect")
#         client_socket, client_addr = sock.accept()
#         print("new client connected")
#         command, data = recv_message_and_parse(client_socket)
#         print(f'command: {command}, data: {data}')
#         while handle_client_message(client_socket, command, data) and command != "LOGOUT":
#             command, data = recv_message_and_parse(client_socket)
#
#
# if __name__ == '__main__':
#     main()
import os
os.remove("C:\\Users\\USER\\PycharmProjects\\broken_telephone\\first.sav")