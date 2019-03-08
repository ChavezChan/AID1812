from socket import *
import sys
import getpass

#创建网络连接，进入程序一级界面
def main():
    if len(sys.argv) < 3:
        print("Argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    s = socket()
    try:
        s.connect((HOST,PORT))
    except Exception as e:
        print(e)
        return
    
    while True :
        print('''
        ==================Welcome==================
        --１、注册　   　２、登陆   　　３、退出 --
        ===========================================
        ''')

        try:
            cmd = int(input("输入选项："))
        except Exception as e:
            print("命令错误")
            continue
        if cmd not in [1,2,3]:
            print("请输入正确的选项")
            continue
        elif cmd == 1:
            do_register(s)
        elif cmd == 2:
            do_login(s)
        elif cmd == 3:
            s.send(b'E')
            print("谢谢使用")
            break

#登陆过程
def do_login(s):
    name = input("User:")
    passwd = getpass.getpass()
    msg = "L %s %s" % (name,passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == "OK":
        print("登陆成功")
        login(s,name)
    else:
        print("登陆失败")
        return


#注册过程
def do_register(s):
    while True:
        name = input("User:")
        passwd = getpass.getpass()
        passwd1 = getpass.getpass("Again:")
        if (" " in name) or (" " in passwd):
            print("用户名密码不允许使用空格")
            continue
        if passwd != passwd1:
            print("两次密码不一致")
            continue
        
        msg = "R %s %s" % (name,passwd)
        #发送请求
        s.send(msg.encode())
        #等待请求
        data = s.recv(128).decode()
        if data == "OK":
            print("注册成功")
            # login(s,name) #注册成功进入二级页面
        elif data == "EXISTS":
            print("用户已存在")
        else:
            print("注册失败")
        return

#登陆成功后进入二级页面
def login(s,name):
     while True :
        print('''
        ==================Welcome==================
        --１、查词　 　２、历史记录 　  ３、注销 --
        ===========================================
        ''')

        try:
            cmd = int(input("输入选项："))
        except Exception as e:
            print("命令错误")
            continue
        if cmd not in [1,2,3]:
            print("请输入正确的选项")
            continue
        elif cmd == 1:
            do_query(s,name)
        elif cmd == 2:
            do_hist(s,name)
        elif cmd == 3:
            return

def do_hist(s,name):
    msg = "H %s " % name
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == "OK":
        while True:
            data = s.recv(1024).decode()
            if data == "##":
                break
            print(data)
    else:
        print("没有历史记录")

def do_query(s,name):
    while True:
        word = input("单词：")
        if word == '##':
            break
        msg = "Q %s %s" % (name,word)
        s.send(msg.encode())
        #可能是单词解释，也可能是找不到
        data = s.recv(2048).decode()
        print(data)

if __name__ == "__main__":
    main()