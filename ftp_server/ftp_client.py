from socket import *
import sys,os
import time 

#具体功能
class FtpClient(object):
    def __init__(self,sockfd):
        self.sockfd = sockfd
    
    def do_list(self):
        time.sleep(0.1)
        self.sockfd.send(b'L') #发送请求
        #等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            data = self.sockfd.recv(4096).decode()
            files = data.split(",")
            for file in files:
                print(file)
        else:
            #无法完成操作
            print(data)
    
    def do_get(self,filename):
        self.sockfd.send(("G "+filename).encode())
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            df = open(filename,"wb")
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":
                    break
                df.write(data)
            df.close()
        else:
            print(data)
    
    def do_put(self,filename):
        if os.path.isfile(filename):
            time.sleep(0.1)
            self.sockfd.send(("B "+filename).encode())
            try:
                df = open(filename,"rb")
            except IOError:
                print("文件不存在")
                return
            while True:
                data = df.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b'##')
                    break
                self.sockfd.send(data)
            df.close()
        else:
            print("不允许上传普通文件以外的文件")

    def do_quit(self):
        self.sockfd.send(b'Q')
        self.sockfd.close()
        sys.exit("谢谢使用")

#网络连接
def main():
    #服务器地址
    ADDR = ("176.113.22.207",8888)
    sockfd = socket()
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print("连接服务器失败：",e)
        return

    #创建文件处理类对象
    ftp = FtpClient(sockfd)

    while True:
        print("\n=================命令选项=================")
        print("***                list                 ***")
        print("***              get  file              ***")
        print("***              put  file              ***")
        print("***                quit                 ***")
        print("===========================================")
        cmd = input("输入命令>>")
        sockfd.send(cmd.encode())
        if cmd.strip() == "list":
            ftp.do_list()
        elif cmd[:3] == "get":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_get(filename)
        elif cmd[:3] == "put":
            filename = cmd.strip().split(" ")[-1]
            ftp.do_put(filename)
        elif cmd.strip() == "quit":
            ftp.do_quit()
        else:
            print("请输入正确命令")

    sockfd.close()

if __name__ == "__main__":
    main()