from time import time

def log_print(msg_type, msg):

    if msg_type == 'send':
        msg_color = '\033[93m'
    elif msg_type == 'recv':
        msg_color = '\033[92m'
    else:
        msg_color = '\033[95m'

    print('%s[%s]: \033[0m%s' % (msg_color, msg_type.upper(), msg))