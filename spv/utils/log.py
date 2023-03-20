from time import time, strftime, localtime


def log_print(msg_type, msg):
    date = strftime("%d/%m/%Y %H:%M:%S", localtime(time()))
    print("%s [%s]: %s" % (date, msg_type.upper(), msg))
