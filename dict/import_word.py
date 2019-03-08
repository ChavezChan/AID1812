'''
导入　单词－解释　到数据库
'''
# dict
# hist
# user
# words
import pymysql
host = 'localhost'
user = 'root'
passwd = '123456'
db = 'dict'

conn = pymysql.connect(host,user,passwd,db)
cursor = conn.cursor()

f = open("dict.txt","r")
a = 0
for data in f:
    word = data.strip().split(" ")[0]
    mean = " ".join(data.strip().split(" ")[1:]).strip()
    mean = mean.replace("'","\\'")

    # print(word,m)

    sql = "insert into words(word,mean) values('%s','%s');" % (word,mean)
    try:
        result = cursor.execute(sql)
        conn.commit()
    except Exception: 
        conn.rollback()



cursor.close()
conn.close()
f.close