from socket import *
import sys
import signal
import os
import glob
import pickle

SERVER_PORT = 9100

USERS_LIST={}

def loadUsers():
    global USERS_LIST
    if os.path.isfile('users.dc') and (os.path.getsize('users.dc') > 0):
        with open('users.dc', 'rb') as input:
            USERS_LIST = pickle.load(input)
    print('USER LIST:')
    for k, v in USERS_LIST.items():
        print(k, v)

def createSocket():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('',SERVER_PORT))
    s.listen(5)
    print('Socket criado!\n')
    return s

def servidor():
    skt=createSocket()
    loadUsers()
    while 1:
        client,address=skt.accept()
        pid = os.fork()
        if pid==0:
            action(client)
            skt.close()
            sys.exit(0)
                    
def action(client):
    option,username,password=processaInfo(client)
    
    if option[0]=='L':
        login(client,username,password)
    elif option[0] =='R':
        registar(client,username,password)
    elif option[0] =='C':
        convidado(client,username)

def processaInfo(client):
    option = ''
    username = ''
    password = ''
    aux = client.recv(32).decode('utf-8')
    option=aux[0]
    i=2
    while 1:
        if aux[i]!=';':
            username+=aux[i]
            i+=1
        else:
            break
    for c in aux[i+1:]:
        password+=c
    return option,username,password
    
def registar(client,username,password):
    global USERS_LIST
    if username not in USERS_LIST.keys():
        USERS_LIST[username]=password
        with open('users.dc', 'wb') as file:
            pickle.dump(USERS_LIST, file, pickle.HIGHEST_PROTOCOL)     
        client.send(('1').encode('utf-8'))
        print('Novo utilizador criado com sucesso:')
        print(username,password)
    else:
        client.send(('0').encode('utf-8'))

def login(client,username,password):
    global USERS_LIST
    if username in USERS_LIST.keys():
        if USERS_LIST[username]==password:
            client.send(('1').encode('utf-8'))
            print('Utilizador conectado com sucesso:')
            print(username,password)
            action_user(client,username,1)
    else:
        client.send(('0').encode('utf-8'))

def action_user(client,username,tipo_user):
    if tipo_user==1:
        if not os.path.exists("users/"+username):
            os.makedirs("users/"+username)
        os.chdir("users/"+username)
    else:
        if not os.path.exists("default"):
            os.makedirs("default")
        os.chdir("default")
        
    flag=1
    while flag:
        if tipo_user==1:
            option=client.recv(20).decode('utf-8')
        else:
            option=username
        if option=='LIST':
            print('Comando LIST recebido!')
            file_list=' '
            for file in glob.glob("*.*"):
                file_list+=file
                file_list+=', '
            client.send((file_list).encode('utf-8'))
        elif option=='DOWNLOAD':
            print('Comando DOWNLOAD recebido!')
            client.send('1'.encode('utf-8'))            
            file_name=client.recv(32).decode('utf-8')
            if file_name in glob.glob("*.*"):
                statinfo = os.stat(file_name)
                client.send(str(statinfo.st_size).encode('utf-8'))  
                sync=client.recv(2).decode('utf-8')
                f = open(file_name,'rb')
                l = f.read(1024)
                while l:
                    client.send(l)
                    l = f.read(1024)             
                f.close()
                print('Ficheiro enviado')
            else:
                client.send('0'.encode('utf-8'))
                print('Ficheiro nao encontrado')
        elif option=='UPLOAD':
            print('Comando UPLOAD recebido!')    
            client.send('1'.encode('utf-8'))
            file_info=client.recv(64).decode('utf-8').split(';')
            client.send('1'.encode('utf-8'))
            file_name=file_info[0]
            size=eval(file_info[1])
            if size>0:
                f = open(file_name,'wb')
                size_received=0
                while size_received<size:
                    l = client.recv(1024)
                    f.write(l)
                    size_received+=len(l)
                f.close()
                client.send('1'.encode('utf-8'))
                print('Ficheiro recebido')
            else:
                print('Erro a receber ficheiro')
        elif option=='QUIT':
            print('Utilizador desconectou-se!')
            os.chdir('../..')
        if tipo_user!=1:
            os.chdir('..')
            flag=0        

def convidado(client,username):
    action_user(client,username,0)
    
def signal_handler(signal, frame):
    print(' pressed...exiting now')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    servidor()