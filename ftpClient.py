import socket
from getpass import getpass
import os
import random
import re

print()
print('--------------------------------------------')
print('\t FTP Client')
print('\t Written by Clocky(AnhLT)')
print('\t lthienanh@gmail.com')
print('\t https://github.com/ClockCorpse')
print('--------------------------------------------')
print()

server = '127.0.0.1'
host = '0.0.0.0'
commandPort = 21
dataPort = 36247
cwd = os.path.expanduser('~')+'/Downloads'
# Use to send login infomation to server
def login(USER,socket):
    socket.send(bytes('USER '+ USER,'ASCII')+b'\x0d\x0a')
    socket.settimeout(1.0)
    res = socket.recv(1024)
    print(res.decode('ASCII'),end = '')
    PASS = getpass('Enter password: ')
    socket.send(bytes('PASS '+ PASS,'ASCII')+b'\x0d\x0a')
    socket.settimeout(1.0)
    res = socket.recv(1024)
    print(res.decode('ASCII'),end = '')
    if int(res.decode('ASCII')[:3]) == 230:
        return True
    else:
        return False

# Use to logout of server
def logout(socket):
    socket.send(bytes('QUIT','ASCII')+b'\x0d\x0a')
    res = socket.recv(1024)
    print(res.decode('ASCII'),end= '')
    socket.close()

def splitBytes(port):
    return divmod(port,0x100)

# Use to initiate data port
def port(socket,portnumber):
    high,low = splitBytes(portnumber)
    client = socket.getsockname()[0]
    octet = client.split('.')
    socket.send(bytes('PORT '+octet[0]+','+octet[1]+','+octet[2]+','+octet[3]+','+str(high)+','+str(low),'ASCII')+b'\x0d\x0a')
    data = socket.recv(1024)
    print(data.decode('ASCII'),end='')
    if int(data.decode('ASCII')[:3]) == 200:
        return True
    else:
        return False
        
# User to retreive file from server
def retr(filePath,commandSocket):
    fileName = re.split(r' |/|\\',filePath)[-1]
    print(fileName)
    dataSocket = socket.socket()
    dataPort = random.randint(50000,65000)
    dataSocket.bind((host,dataPort))      
    if port(commandSocket,dataPort) == True:
        commandSocket.send(bytes('RETR '+filePath,'ASCII')+b'\x0d\x0a')
        try:
            commandSocket.settimeout(2)
            cmdData = commandSocket.recv(1024)
        except:
            pass
        print(cmdData.decode('ASCII'),end='')
        dataSocket.listen(1)
        c,addr = dataSocket.accept()
        with open(cwd+'/'+fileName,'wb') as f:
            while True:
                maxLen = 1460
                data = c.recv(maxLen)
                f.write(data)
                if len(data)==0:
                    break
        f.close()
        try:
            cmdData = commandSocket.recv(1024)
            print(cmdData.decode('ASCII'),end='')
        except:
            pass
        dataSocket.close()

def changeLocalDir(cmd,commandSocket):
    global cwd
    if cmd[4:]=='':
        print('Current local directory: ' + cwd)
    else:
        if os.path.exists(cwd+'/'+cmd[4:]):
            cwd = cwd+'/'+cmd[4:]
            print('Current local directory: ' + cwd)
        else:
            print('Directory does not exists!')


# similar to switch case
# def options(cmd,commandSocket):
#     switcher = {
#         'get':retr(cmd,commandSocket),
#         'dir':getDir(commandSocket),
#     }
#     return switcher.get(cmd[:3],'invalid command')

def getDir(commandSocket):
    dataSocket = socket.socket()
    dataPort = random.randint(50000,65000)
    dataSocket.bind((host,dataPort))
    dataSocket.listen(1)
    if port(commandSocket,dataPort)==True:
        dataSocket.settimeout(2.0)
        commandSocket.send(bytes('LIST','ASCII')+b'\x0d\x0a')
        c,addr = dataSocket.accept()
        cmdData = commandSocket.recv(1024)
        print(cmdData.decode('ASCII'),end='')
        while True:
                c.settimeout(2.0)
                data = c.recv(1024)
                print(data.decode('ASCII'),end='')
                if len(data) == 0:
                    break
        try:
            commandSocket.settimeout(0.1)
            cmdData = commandSocket.recv(1024)
            print(cmdData.decode('ASCII'),end='')
        except:
            pass
    dataSocket.close()      

def changeDir(path,commandSocket):
    commandSocket.send(bytes('CWD '+path,'ASCII')+b'\x0d\x0a')
    response = commandSocket.recv(1024)
    response = response.decode('ASCII')
    print(response,end='')
    if int(response[:3]) == 250:
        return True
    else:
        return False

def manual():
    print('\tget [FILE NAME] \t-- Retrieve file from remote server.')
    print("\tdir \t\t\t-- Get remote server's directory.")
    print('\tlcd [PATH] \t\t-- Change local directory.')
    print('\tlcd \t\t\t-- Shows local current working directory.')
    print('\thelp \t\t\t-- How the hell did you get here?')

def stor(filePath,cwd,commandSocket):
    cwd = cwd + '/' + filePath
    if os.path.isfile(cwd):
        fileName = re.split(r' |/|\\',filePath)[-1]
        dataSocket = socket.socket()
        dataPort = random.randint(50000,65000)
        dataSocket.bind((host,dataPort))
        dataSocket.listen(1)
        if port(commandSocket,dataPort) == True:
            dataSocket.settimeout(2.0)
            commandSocket.send(bytes('STOR '+fileName,'ASCII')+b'\x0d\x0a')
            data = commandSocket.recv(1024).decode('ASCII')
            print(data,end='')
            if int(data[:3]) == 125:
                c,addr = dataSocket.accept()
                with open(cwd,'rb') as f:
                    bytesToSend = f.read(1460)
                    c.send(bytesToSend)
                    while bytesToSend !="":
                        bytesToSend = f.read(1460)
                        if bytesToSend == b'':
                            f.close()
                            break
                        c.send(bytesToSend)
                try:
                    dataSocket.close()
                    commandSocket.settimeout(0.1)
                    cmdData = commandSocket.recv(1024)
                    print(cmdData.decode('ASCII'),end='')
                except:
                    pass
    else:
        print('File does not exists!')

def makeDir(folderName):
    if os.path.exists(cwd+'/'+folderName):
        print('Folder already exists!')
    else:
        os.mkdir(cwd+'/'+folderName)

def localdir():
    listfile = os.listdir(cwd)
    for fil in listfile:
        print(fil)
def rmDir(folderName):
    if os.path.exists(cwd+'/'+folderName):
        shutil.rmtree(cwd+'/'+folderName)
    else:
        print("Folder doesn't exists!")


def Main():
    server = input("Enter server's IP: ")
    commandSocket = socket.socket()
    fileName = ''
    try:
        commandSocket.settimeout(10.0)
        commandSocket.connect((server,commandPort))
        data = commandSocket.recv(1024)
        print(data.decode('ASCII'),end = '')
        try:
            commandSocket.settimeout(0.01)
            data = commandSocket.recv(1024)
            print(data.decode('ASCII'),end = '')
        except:
            print('',end='')
        USER = input('Enter username: ')
        if login(USER,commandSocket) == True:
            while True:
                cmd = input('ftp> ')
                if cmd[:3]=='get':
                    retr(cmd[4:],commandSocket)
                    try:
                        commandSocket.settimeout(1.0)
                        print(commandSocket.recv(1024).decode('ASCII'),end='')
                    except:
                        pass
                if cmd[:3]=='dir':
                    getDir(commandSocket)
                    try:
                        print(commandSocket.recv(1024).decode('ASCII'),end='')
                    except:
                        pass
                if cmd[:2]=='cd':
                    changeDir(cmd[3:],commandSocket)
                if cmd[:3]=='lcd':
                    changeLocalDir(cmd,commandSocket)
                if cmd[:4]=='help':
                    manual()
                if cmd[:4] == 'ldir':
                    localdir()
                if cmd[:5]== 'mkdir':
                    makeDir(cmd[6:])
                if cmd[:5]== 'rmdir':
                    rmDir(cmd[6:])
                if cmd[:3]=='put':
                    stor(cmd[4:],cwd,commandSocket)
                    try:
                        commandSocket.settimeout(1.0)
                        print(commandSocket.recv(1024).decode('ASCII'),end='')
                    except:
                        pass
                if cmd == 'quit':
                    try:
                        logout(commandSocket)
                        break
                    except:
                        print('Server timeout!')
                        break
                #options(cmd,commandSocket)
        commandSocket.close()
    except:
        print('Unable to connect to server!')

if __name__ == '__main__':
    Main()
