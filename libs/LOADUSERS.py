class loadUsers():
    def __init__(self, UsersFile, UserList):
        # SETTINGS_FILE = 'Settings.txt'
        # USERLIST = []
        # USERFILE = "setup/Users.txt"

        #User:Password
        try:

            f1 = open(UsersFile,'r')
            text = str(f1.read())
            f1.close()

            StartInd = text.find("[") +1
            StopInd = text.find("]")
            text = str(text[StartInd:StopInd])

            text = text.split(',')
            for x in enumerate(text):
                #print x[1]
                Xinfo = str(x[1])
                try:
                    Xinfo = Xinfo.replace(" ", "")
                    Xinfo = Xinfo.replace("\'", "")
                    Xinfo = Xinfo.replace("\"", "")
                    Xinfo = Xinfo.replace("[", "")
                    Xinfo = Xinfo.replace("]", "")
                    #Xinfo = Xinfo.upper()

                    if (Xinfo== ""):
                        break

                    if (len(Xinfo) <0):
                        break
                    else:
                        UserList.append(Xinfo)

                except:
                    pass
        except:
            print ("<Users.txt file not found>")
            print ("<Creating Users.txt with default user credentials>")
            f1 = open(UsersFile,'w')
            f1.write("<USERS>")
            f1.close()
