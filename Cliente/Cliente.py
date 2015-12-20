from socket import *
import sys
import signal
import os
import glob

SERVER_NAME = 'localhost'
SERVER_PORT = 9100
CACHE_NAME = 'localhost'
CACHE_PORT = 9101

def menu():
    while 1:
        os.system('clear')
        print('|--------------------------------------|')
        print('|-----------------MENU-----------------|')
        print('|--------------------------------------|')
        print('1-Login.')
        print('2-Registar.')
        print('3-Entrar como convidado.')
        print('0-Sair.')
        option = eval(input('Insira o numero da operacao a executar:'))
        while option < 0 or option > 3:
            option = eval(input("Escolha uma das opções anteriores: "))
        if option==1:
            skt=createSocket()            
            login(skt)
            skt.close()
        elif option==2:
            skt=createSocket()
            registar(skt)
            skt.close()
        elif option==3:
            skt_c=createSocket_c()
            convidado(skt_c)
            skt_c.close()
        else:
            break

def menu_user(skt):
    flag=1
    while flag:
        os.system('clear')
        print('|--------------------------------------|')
        print('|--------------UTILIZADOR--------------|')
        print('|--------------------------------------|')
        print('1-LIST-Listar ficheiros disponiveis.')
        print('2-DOWNLOAD-Download ficheiro.')
        print('3-UPLOAD-Upload ficheiro.')
        print('0-QUIT-Logout.')
        option = eval(input('Insira o numero da operacao a executar:'))
        while option < 0 or option > 3:
            option = eval(input("Escolha uma das opções anteriores: "))
        if option==1:
            skt.send("LIST".encode('utf-8'))
            lista=skt.recv(1024).decode('utf-8')
            print('Lista de ficheiros')
            print(lista)
        elif option==2:
            skt.send("DOWNLOAD".encode('utf-8'))
            sync=skt.recv(2).decode('utf-8')
            filename = input('Insira o nome do ficheiro a fazer download:')
            skt.send(filename.encode('utf-8'))
            size=eval(skt.recv(16).decode('utf-8'))
            skt.send('1'.encode('utf-8'))
            if size>=0:
                print('Ficheiro encontrado')
                f = open(filename,'wb')
                size_received=0
                while size_received<size:
                    l = skt.recv(1024)
                    f.write(l)
                    size_received+=len(l)
                f.close()
                print('Ficheiro recebido')
            else:
                print('Ficheiro nao encontrado')
            
        elif option==3:
            filename = input('Insira o nome do ficheiro a fazer upload:')
            if filename in glob.glob("*.*"):                
                statinfo = os.stat(filename)
                if statinfo.st_size >0:
                    skt.send("UPLOAD".encode('utf-8'))
                    sync=skt.recv(2).decode('utf-8')
                    skt.send((filename+';'+str(statinfo.st_size)).encode('utf-8'))
                    sync=skt.recv(2).decode('utf-8')                
                    f = open(filename,'rb')
                    l = f.read(1024)
                    while l:
                        skt.send(l)
                        l = f.read(1024)                
                    f.close()
                    status=skt.recv(2).decode('utf-8');
                    if status == '1':
                        print('Ficheiro enviado')
                    else:
                        print('Erro no envio')
                else:
                    print('Ficheiro vazio')
            else:
                print('Ficheiro nao encontrado')            
        else:
            skt.send("QUIT".encode('utf-8'))
            flag=0



def registar(skt):
    os.system('clear')
    print('|--------------------------------------|')
    print('|----------------REGISTO---------------|')
    print('|--------------------------------------|')
    username = input('ID:')
    password = input('PW:')
    skt.send(('R;'+username+';'+password).encode('utf-8'))
    status=skt.recv(5).decode('utf-8')
    print(status)
    if status == '1':
        print('Registado com sucesso!')
    else:
        print('Erro no registo!')
	
def login(skt):
    os.system('clear')
    print('|--------------------------------------|')
    print('|-----------------LOGIN----------------|')
    print('|--------------------------------------|')
    username = input('ID:')
    password = input('PW:')
    skt.send(('L;'+username+';'+password).encode('utf-8'))
    status=skt.recv(5).decode('utf-8')
    if status == '1':
        print('Conectado com sucesso!')
        menu_user(skt)
    else:
        print('Erro no login!')
	
def convidado(skt_c):
    os.system('clear')
    print('|--------------------------------------|')
    print('|----------------DEFAULT---------------|')
    print('|--------------------------------------|')
    status=skt_c.recv(5).decode('utf-8')
    if status == '1':
        print('Conectado com sucesso!')
        menu_user(skt_c)
    else:
        print('Erro na conexao!')
def createSocket():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.connect((SERVER_NAME, SERVER_PORT))
    print('Socket criado!\n')
    return s

def createSocket_c():
    s_c = socket(AF_INET, SOCK_STREAM)
    s_c.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s_c.connect((CACHE_NAME, CACHE_PORT))
    print('Socket Cache criado!\n')
    return s_c


def signal_handler(signal, frame):
    print(' pressed...exiting now')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    menu()