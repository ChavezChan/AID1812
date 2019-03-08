'''
dict project fro AID
'''
from socket import *
import pymysql
import os,sys
import time
import signal

#定义全局变量
if len(sys.argv) < 3:
    print('''
    Start as:
    python3 dict_server.py 0.0.0.0 8000
    ''')
    sys.exit(0)

HOST = sys.argv[1]
PORT = int(sys.argv[2])
ADDR = (HOST,PORT)
DICT_TEXT = "./dict.txt"

#搭建网络连接
def main():
    # 连接数据库
    db = pymysql.connect("localhost","root","123456","dict")
    # 创建套接字
    s = socket()
    # s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    #僵尸进程处理
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()
            print("Connect from",addr)
        except KeyboardInterrupt:
            c.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue

        #创建子进程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c,db)
            sys.exit()
        else:
            c.close()

def do_register(c,db,data):
    l = data.split(" ")
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    
    sql = "select * from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r != None:
        c.send(b'EXISTS')
        return

    #插入用户
    sql = "insert into user(name,passwd) values('%s','%s')" % (name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FAIL')

def do_login(c,db,data):
    l = data.split(" ")
    print(l)
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    sql = "select * from user where name='%s' and passwd='%s'" % (name,passwd)
    cursor.execute(sql)
    r = cursor.fetchone()
    if r == None:
        c.send(b'FAIL')
    else:
        c.send(b'OK')

def do_query(c,db,data):
    l = data.split(" ")
    name = l[1]
    word = l[2]

    #插入历史记录
    cursor = db.cursor()
    tm = time.ctime()
    sql = "insert into hist(name,word,time) values('%s','%s','%s')" % (name,word,tm)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

    #用数据库查找
    sql = "select * from words where word='%s'" % word
    cursor.execute(sql)
    tmp = cursor.fetchall()
    if not tmp:
        c.send("没有找到该单词".encode())
        return
    for i in tmp:
        s = i[1] + "------>" + i[2]
        c.send(s.encode())

    # #单词本查找
    # f = open(DICT_TEXT)
    # for line in f:
    #     tmp = line.split(" ")[0]
    #     if tmp > word:
    #         break
    #     elif tmp == word:
    #         c.send(line.encode())
    #         f.close
    #         return
    # c.send("没有找到该单词".encode())
    # f.close()

def di_hist(c,db,data):
    name = data.split(" ")[1]
    cursor = db.cursor()
    sql = "select * from hist where name='%s' order by id desc limit 10" % name
    print(sql)
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b'FAIL')
        return
    else:
        c.send(b'OK')
        time.sleep(0.1)
    
    for i in r:
        msg = "%s  %s  %s" % (i[1],i[2],i[3])
        c.send(msg.encode())
        time.sleep(0.1)
    c.send(b"##")



#处理客户端请求
def do_child(c,db):
    while True:
        data = c.recv(1024).decode()
        print(c.getpeername(),":",data)
        if not data or data[0] == 'E':
            c.close()
            sys.exit()
        elif data[0] == "R":
            do_register(c,db,data)
        elif data[0] == "L":
            do_login(c,db,data)
        elif data[0] == "Q":
            print(123)
            do_query(c,db,data)
        elif data[0] == "H":
            di_hist(c,db,data)

if __name__ == "__main__":
    main()