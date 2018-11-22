def ls():
    msg = os.listdir(os.getcwd())
    msg = "\n".join(msg)
    print_debug(msg)
    send_msg("ls", msg)
