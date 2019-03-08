'''
ftp 文件服务器
fork server
'''
from socket import *
import os,sys
import signal
import time

#全局变量
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST,PORT)
FILE_PATH = "/home/tarena/TESTDIR/"

class FtpServer(object):
    def __init__(self,connfd):
        self.connfd = connfd

    def do_list(self):
        #获取文件列表
        file_list = os.listdir(FILE_PATH)
        print(file_list)
        if not file_list:
            self.connfd.send("文件库为空".encode())
        else:
            self.connfd.send("OK".encode())
            time.sleep(0.1)

        files = ""
        for file in file_list:
            if file[0] != "." and os.path.isfile(FILE_PATH+file):
                files = files + file + ","

        #将拼接好的字符串传给客户端
        self.connfd.send(files.encode())

    def do_get(self,filename):
        try:
            df = open(FILE_PATH+filename,"rb")
        except IOError:
            self.connfd.send("文件不存在".encode())
            return
        else:
            self.connfd.send(b'OK')
            time.sleep(0.1)
        #发送文件内容
        while True:
            data = df.read(1024)
            if not data:
                df.close()
                time.sleep(0.1)
                self.connfd.send(b"##")
                return
            self.connfd.send(data)
        df.close()
        
    def do_put(self,filename):
        df = open(FILE_PATH+filename,"wb")
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                df.close()
                return
            df.write(data)
        df.close()

def do_request(connfd):
    ftp = FtpServer(connfd)
    while True:
        data = connfd.recv(1024).decode()
        print(data)
        #退出程序
        if not data or data[0] == "Q":
            connfd.close()
            return   
        if data[0] == 'L':
            ftp.do_list()
        elif data[0] == "G":
            filename = data.split(" ")[-1]
            ftp.do_get(filename)
        elif data[0] == "B":
            filename = data.split(" ")[-1]
            ftp.do_put(filename)

#网络搭建
def main():
    #创建套接字
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)
    print("Listen the port 8888...")
    signal.signal(signal.SIGCLD,signal.SIG_IGN)
    while True:
        try:
            connfd,addr = sockfd.accept()
        except KeyboardInterrupt:
            sockfd.close()
            sys.exit("服务器退出")
        except Exception as e:
            print("服务器异常",e)
            continue
        print("连接客户端：",addr)
        #创建子进程
        pid = os.fork()
        if pid == 0:
            sockfd.close()
            do_request(connfd)
            os._exit(0)
        else:
            connfd.close()

if __name__ == "__main__":
    main()