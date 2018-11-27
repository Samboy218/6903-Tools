#Show all files that have been made/changed since the last call
#only works on linux right now
SETTINGS["newFilesTimestamp"] = {}
def newFiles(start="/"):
    send_msg("newFiles", "checking {} for new shit".format(start))
    output = []
    time_stamp = SETTINGS['newFilesTimestamp'].get(start, None)
    if time_stamp is None:
        time_stamp = 0
    for root, dirs, files in os.walk(start):
        for name in files:
            f = os.path.join(root, name)
            
            try:
                stats = os.stat(f)
            except:
                continue
            mask = 0
            #access
            if stats.st_atime > time_stamp:
                mask += 1
            #modify
            if stats.st_mtime > time_stamp:
                mask += 2
            #metadata change
            if stats.st_ctime > time_stamp:
                mask += 4
            if mask:
                output.append("["+str(mask)+"]" + f)
    SETTINGS["newFilesTimestamp"][start] = time.time()
    send_msg("newFiles", ("\n".join(output)).encode('ascii', 'ignore').decode('ascii'))
    return
