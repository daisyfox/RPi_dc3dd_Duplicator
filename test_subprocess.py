import subprocess
import time

#---------------------------------------------------------
#           Obtaining a Directory Listing
#---------------------------------------------------------

def directoryListing(version):
    if version == "1":
        ##  v1 'check_output' - tested
        output = subprocess.check_output(['ls'])
        output = output.decode(encoding = "ascii", errors = "ignore")
        print(output)

    elif version == "2a":
        ## v2a 'Popen' - tested
        myProcess = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
        item1, item2 = myProcess.communicate()
        output = item1.decode(encoding = "ascii", errors = "ignore")
        print(output)

    elif version == "2b":
        ## v2b 'Popen' - tested
        cmdtext = "ls"
        myProcess = subprocess.Popen([cmdtext], stdout=subprocess.PIPE)
        item1, item2 = myProcess.communicate()
        output = item1.decode(encoding = "ascii", errors = "ignore")
        print(output)

    elif version == "2c":
        ## v2c 'Popen' - tested
        cmdtext = "ls"
        myProcess = subprocess.Popen([cmdtext], stdout=subprocess.PIPE)
        output = myProcess.communicate()[0].decode(encoding = "ascii", errors = "ignore")
        print(output)
        print(myProcess.returncode)

    elif version == "2d":
        ## v2d 'Popen' - tested
        cmdtext = ["ls", "-l"]
        myProcess = subprocess.Popen(cmdtext, stdout=subprocess.PIPE)
        
        while True:
            output = myProcess.stdout.readline().decode(encoding = "ascii", errors = "ignore")
            if output == "" and myProcess.poll() != None: # 'None' indicates subprocess is still running
                break
            else:
                print(output.strip())

    elif version == "3a":
        ## v3a 'getoutput' - tested
        output = subprocess.getoutput("ls")
        print(output)

    elif version == "3b":
        ## v3b 'getoutput' - tested
        cmdtext = "ls"
        output = subprocess.getoutput(cmdtext)
        print(output)

#---------------------------------------------------------
#           Copy a file using dc3dd
#---------------------------------------------------------

def copyDirectory(version):
    if version == "1":
        ##  v1 'getoutput' - tested
        output = subprocess.getoutput("dc3dd if=/home/pi/Duplicator/Duplicator_v1.py of=/media/USB_BCT1/Duplicator/Duplicator_v1.py")
        print(output)

    elif version == "2a":
        ##  v2a 'getoutput' / variable cmdtext - tested
        cmdtext = "dc3dd if=/home/pi/Duplicator/Duplicator_v1.py of=/media/USB_BCT1/Duplicator/Duplicator_v1.py"
        output = subprocess.getoutput(cmdtext)
        print(output)

    elif version == "2b":
        ##  v2b 'getoutput' / variable cmdtext (list) - tested
        cmdtext = []
        cmdtext.append("dc3dd if=/home/pi/Duplicator/dup_icon.png of=/media/USB_BCT1/Duplicator/dup_icon.png") 
        cmdtext.append("dc3dd if=/home/pi/Duplicator/Duplicator_v1.py of=/media/USB_BCT1/Duplicator/Duplicator_v1.py")
        print(cmdtext)
        for i in range(len(cmdtext)):
            output = subprocess.getoutput(cmdtext[i])
            if output.find("[!!]") >= 0:
                print("\n\n**  ERRORS OCCURRED  **")
            print(output)
            if output.find("[!!]") >= 0:
                print("** ERRORS OCCURRED  **\n\n")          

    elif version == "2c":
        ## v2c 'Popen' - tested
        cmdtext = ["dc3dd", "if=/home/pi/Duplicator/dup_icon.png", "of=/media/USB_BCT1/Duplicator/dup_icon.png"]
        myProcess = subprocess.Popen(cmdtext, stderr=subprocess.PIPE) # dd & dc3dd send to stderr !
        
        while True:
            output = myProcess.stderr.readline().decode(encoding = "ascii", errors = "ignore")
            if output.find('\r') >= 0:
                print("OVERWRITE NEXT LINE . . . .")
            info = output.strip('\n')
            info = info.replace('  ', '')
            if output == "" and myProcess.poll() != None: # 'None' indicates subprocess is still running
                break
            else:
                print(info)

    elif version == "2d":
        ## v2d Popen, readline - tested
        cmdtext = []
        cmdtext.append(["dc3dd", "if=/home/pi/Duplicator/dup_icon.png", "of=/media/USB_BCT1/Duplicator/dup_icon.png"]) 
        cmdtext.append(["dc3dd", "if=/home/pi/Duplicator/Duplicator_v1.py", "of=/media/USB_BCT1/Duplicator/Duplicator_v1.py"])

        for i in range(len(cmdtext)):
            myProcess = subprocess.Popen(cmdtext[i], stderr=subprocess.PIPE)
            
            while True:
                output = myProcess.stderr.readline().decode(encoding = "ascii", errors = "ignore")
                if output.find('\r') >= 0:
                    print("OVERWRITE NEXT LINE . . . .")
                info = output.strip('\n')
                info = info.replace('  ', '')
                if output == "" and myProcess.poll() != None: # 'None' indicates subprocess is still running
                    break
                else:
                    print(info)

    elif version == "2e":
        ## v2d Popen, read - not tested
        cmdtext = []
        cmdtext.append(["dc3dd", "if=/home/pi/Duplicator/dup_icon.png", "of=/media/USB_BCT1/Duplicator/dup_icon.png"]) 

        for i in range(len(cmdtext)):
            myProcess = subprocess.Popen(cmdtext[i], stderr=subprocess.PIPE)
            output = ""
            
            while True:
                char = myProcess.stderr.read(1).decode(encoding = "ascii", errors = "ignore")               
                if char == "" and myProcess.poll() != None: # 'None' indicates subprocess is still running
                    break

                output += char
                if output.find('\r') >= 0:
                    print("\rTHIS LINE IS AN OVERWRITING LINE . . . .", end = "\r")
                    output = ""
                elif output.find('\n')>= 0:
                    output = ""
                    print(char, end = "")
                else:
                    print(char, end = "")

                time.sleep(0.01)


#---------------------------------------------------------
#           Zero Drive using dc3dd
#---------------------------------------------------------

def zeroDrive(version):
    if version == "1":
        ##  v1 - not tested
        output = subprocess.getoutput("sudo dd if=/dev/zero of=/dev/sdb1")
        print(output)

    elif version == "2":
        ## v2 - not tested
        cmdtext = "sudo dc3dd if=/dev/zero of=/dev/sdb1"
        myProcess = subprocess.Popen([cmdtext], stdout=subprocess.PIPE)

        while True:
            output = myProcess.stdout.readline().decode(encoding = "ascii", errors = "ignore")
            if output == "" and myProcess.poll() != None: # 'None' indicates subprocess is still running
                break
            else:
                print(output.strip())

#---------------------------------------------------------
#           Clone Drive using dc3dd
#---------------------------------------------------------

def cloneDrive(version):
    if version == "1":
        ##  v1
        output = subprocess.getoutput("sudo dc3dd if=/dev/sda1 of=/dev/sdb1")
        print(output)

    elif version == "2":
        ## v2
        cmdtext = "sudo dc3dd if=/dev/sda1 of=/dev/sdb1"
        myProcess = subprocess.Popen([cmdtext], stdout=subprocess.PIPE)

        while True:
            output = myProcess.stdout.readline().decode(encoding = "ascii", errors = "ignore")
            if output == "" and myProcess.poll() != None: # 'None' indicates subprocess is still running
                break
            else:
                print(output.strip())



########
## MAIN
########
                
#directoryListing("2d")
copyDirectory("2e")
#zeroDrive("2")
#cloneDrive("2")
