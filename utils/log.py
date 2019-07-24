from time import time, strftime, localtime


def log_print(msg_type, msg):

    if msg_type == 'send':
        msg_color = '\033[93m'
    elif msg_type == 'recv':
        msg_color = '\033[92m'
    else:
        msg_color = '\033[95m'

    date = strftime('%d/%m/%Y %H:%M:%S', localtime(time()))

    print('%s %s[%s]: \033[0m%s' % (date, msg_color, msg_type.upper(), msg))
