from socket import *
import sys
import signal
import os
import glob

SERVER_PORT = 9100
SERVER_NAME= 'localhost'
CACHE_PORT = 9101


def cache():
    skt_c=createSocket_c()
    while 1:
        client,address=skt_c.accept()
        pid = os.fork()
        if pid==0:
            action(client)
            skt.close()
            sys.exit(0)

def action(client):
    if not os.path.exists("default"):
        os.makedirs("default")
    os.chdir("default")
        
    flag=1
    client.send(('1').encode('utf-8'))
    while flag:
        option=client.recv(20).decode('utf-8')
        if option=='LIST':
            print('Comando LIST recebido!')
            skt_s=createSocket_s()
            skt_s.send('C:LIST;LIST'.encode('utf-8'))
            file_list=skt_s.recv(1024).decode('utf-8')
            client.send((file_list).encode('utf-8'))
            skt_s.close()
        elif option=='DOWNLOAD':
            print('Comando DOWNLOAD recebido!')
            client.send('1'.encode('utf-8'))
            file_name=client.recv(32).decode('utf-8')           
            if file_name in glob.glob("*.*"):
                statinfo = os.stat(file_name)
                client.send(str(statinfo.st_size).encode('utf-8'))     
                f = open(file_name,'rb')
                l = f.read(1024)
                while l:
                    client.send(l)
                    l = f.read(1024)             
                f.close()
                print('Ficheiro enviado')
            else:
                skt_s=createSocket_s()
                skt_s.send("C;DOWNLOAD;DOWNLOAD".encode('utf-8'))
                sync=skt_s.recv(2).decode('utf-8')
                skt_s.send(file_name.encode('utf-8'))
                size=eval(skt_s.recv(16).decode('utf-8'))
                if size>0:
                    skt_s.send('1'.encode('utf-8'))
                    print('Ficheiro encontrado no servidor')
                    f = open(file_name,'wb')
                    size_received=0
                    while size_received<size:
                        l = skt_s.recv(1024)
                        f.write(l)
                        size_received+=len(l)
                    f.close()
                    print('Ficheiro recebido')
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
                skt_s.close()
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
                skt_s=createSocket_s()
                if file_name in glob.glob("*.*"):
                    skt_s.send("C;UPLOAD;UPLOAD".encode('utf-8'))
                    sync=skt_s.recv(2).decode('utf-8')
                    statinfo = os.stat(file_name)
                    skt_s.send((file_name+';'+str(statinfo.st_size)).encode('utf-8')) 
                    sync=skt_s.recv(2).decode('utf-8')
                    f = open(file_name,'rb')
                    l = f.read(1024)
                    while l:
                        skt_s.send(l)
                        l = f.read(1024)                
                    f.close()
                    status=skt_s.recv(2).decode('utf-8');
                    if status == '1':
                        print('Ficheiro enviado')
                    else:
                        print('Erro no envio')
                    skt_s.close()
                else:
                        print('Ficheiro nao encontrado')                    
            else:
                client.send('0'.encode('utf-8'))
                print('Ficheiro nao encontrado')            
        elif option=='QUIT':
            print('Utilizador desconectou-se!')
            os.chdir('..')

def createSocket_s():
    s_s = socket(AF_INET, SOCK_STREAM)
    s_s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s_s.connect((SERVER_NAME, SERVER_PORT))
    print('Socket criado!\n')
    return s_s

def createSocket_c():
    s_c = socket(AF_INET, SOCK_STREAM)
    s_c.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s_c.bind(('',CACHE_PORT))
    s_c.listen(5)
    print('Socket criado!\n')
    return s_c

def signal_handler(signal, frame):
    print(' pressed...exiting now')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    cache()