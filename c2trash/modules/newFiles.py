#Show all files that have been made/changed since the last call
#only works on linux right now
SETTINGS["newFilesTimestamp"] = 0
def newFiles(start="/"):
    send_msg("newFiles", "checking {} for new shit".format(start))
    output = []
    for root, dirs, files in os.walk(start):
        for name in files:
            f = os.path.join(root, name)
            
            try:
                stats = os.stat(f)
            except:
                continue
            mask = 0
            #access
            if stats.st_atime > SETTINGS["newFilesTimestamp"]:
                mask += 1
            #modify
            if stats.st_mtime > SETTINGS["newFilesTimestamp"]:
                mask += 2
            #metadata change
            if stats.st_ctime > SETTINGS["newFilesTimestamp"]:
                mask += 4
            if mask:
                output.append("["+str(mask)+"]" + f)
    SETTINGS["newFilesTimestamp"] = time.time()
    send_msg("newFiles", ("\n".join(output)).encode('ascii', 'ignore').decode('ascii'))
    return
