# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {"LOGIN", "LOGOUT", "LOGGED", "GET_QUESTION", "SEND_ANSWER", "MY_SCORE", "HIGHSCORE"}

PROTOCOL_SERVER = {"Error!", "LOGIN_OK", "LOGGED+ANSWER", "YOUR_QUESTION", "CORRECT_ANSWER", "WONG_ANSWER", "YOUR_SCORE", "ALL_SCORE", "ERROR", "NO_QUESTIONS"}

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occurred
    """
    if (cmd not in PROTOCOL_CLIENT and cmd not in PROTOCOL_SERVER) or len(data) > 9999:
        return ERROR_RETURN
    elif ((cmd == "LOGIN" or cmd == "SEND_ANSWER") and '|' not in data) or (cmd == "YOUR_QUESTION" and len(data.split('|')) != 7):
        return ERROR_RETURN
    while len(cmd) < 16:
        cmd += " "
    len_msg = str(len(data))
    while len(len_msg) < 4:
        len_msg = '0' + len_msg
    return join_msg([cmd, len_msg, data])


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occurred, returns None, None
    """
    if data == "":
        return ERROR_RETURN, ERROR_RETURN
    cmd = data[:16]
    while cmd[-1] == " ":
        cmd = cmd[:-1]
    while cmd[0] == " " and len(cmd) > 1:
        cmd = cmd[1:]
    if cmd == "LOGIN" or cmd == "SEND_ANSWER":
        fields = split_msg(data, 4)
    elif cmd == "YOUR_QUESTION":
        print('nigger', data)
        fields = split_msg(data, 9)
    else:
        fields = split_msg(data, 3)
    if fields == ERROR_RETURN:
        return ERROR_RETURN, ERROR_RETURN
    cmd, length = fields[:2]
    msg = '|'.join(fields[2:])
    print([cmd, length, msg])
    if len(cmd) != 16 or len(length) != 4 or int(length) != len(msg):
        return ERROR_RETURN, ERROR_RETURN
    while cmd[-1] == " ":
        cmd = cmd[:-1]
    while cmd[0] == " " and len(cmd) > 1:
        cmd = cmd[1:]
    if cmd not in PROTOCOL_SERVER and cmd not in PROTOCOL_CLIENT:
        return ERROR_RETURN, ERROR_RETURN
    return cmd, msg


def split_msg(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's delimiter (|) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    fields = msg.split('|')
    if len(fields) != expected_fields:
        return ERROR_RETURN
    return fields


def join_msg(msg_fields):
    """
    Helper method. Gets a list, joins all of its fields to one string divided by the delimiter.
    Returns: string that looks like cell1|cell2|cell3
    """
    return '|'.join(msg_fields)