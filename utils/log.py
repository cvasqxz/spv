from time import time, strftime, localtime


def log_print(msg_type, msg):

    if "send" in msg_type:
        msg_color = "\033[92m"
    elif "recv" in msg_type:
        msg_color = "\033[93m"
    elif "main" in msg_type:
        msg_color = "\033[91m"
    else:
        msg_color = "\033[95m"

    date = strftime("%d/%m/%Y %H:%M:%S", localtime(time()))

    print("%s %s[%s]: \033[0m%s" % (date, msg_color, msg_type.upper(), msg))
