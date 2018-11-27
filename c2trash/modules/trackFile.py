#tracks a file
#set remove to true to untrack a file
SETTINGS["trackFileList"] = {}
SETTINGS["trackFileInterval"] = 60
def trackFile(fileName, remove=False):
    currTime = time.time()
    #check if file is already tracked
    if SETTINGS["trackFileList"].get(fileName, None) is not None:
        if remove:
            del SETTINGS["trackFileList"][fileName]
            send_msg("trackFile", "Stopped tracking" + fileName + "\n")
        else:
            send_msg("trackFile", "File " + fileName + " already tracked\n")
        return
    #otherwise, add the file to our tracked list
    try:
        stats = os.stat(fileName)
    except:
        send_msg("trackFile", "can't stat file, aborting track\n")
        return
    to_track = {
        "last_seen": currTime,
        "history" : [(currTime, stats.st_atime, stats.st_mtime, stats.st_ctime, 0)]
    }
    SETTINGS["trackFileList"][fileName] = to_track
    send_msg("trackFile", "File "+ fileName +" now being tracked\n")

def trackFiles():
    #for each file we are tracking, check if it has been changed since we looked at it
    for name in SETTINGS["trackFileList"]:
        currTime = time.time()
        try:
            stats = os.stat(name)
        except:
            #file is gone?
            continue
        lastChecked = SETTINGS["trackFileList"][name]["history"][-1]
        mask = 0
        if stats.st_atime > lastChecked[1]:
            mask += 1

        if stats.st_mtime > lastChecked[2]:
            mask += 2

        if stats.st_ctime > lastChecked[3]:
            mask += 4
        if mask > 0:
            SETTINGS["trackFileList"][name]["history"].append((currTime, stats.st_atime, stats.st_mtime, stats.st_ctime, mask))
        SETTINGS["trackFileList"][name]["last_seen"] = currTime
        #requeue self onto eventqueue
        return

def getTrackedFiles(fName=None):
    #if no name is specified, get all tracked files
    toReport = []
    output = ""
    if fName is None:
        for name in SETTINGS["trackFileList"].keys():
            toReport.append(name)
    else:
        toReport.append(fName)

    for name in toReport:
        #format what we have
        output += "Report for " + name + ":\n"
        output += "Last Seen: " + str(SETTINGS["trackFileList"][name]["last_seen"]) + "\n"
        for item in SETTINGS["trackFileList"][name]["history"]:
            output += repr(item) + "\n"

    send_msg("getTrackedFiles", output.encode('ascii', 'ignore').decode('ascii'))
    return
