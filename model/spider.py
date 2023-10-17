import requests 
from bs4 import BeautifulSoup
import json
import sqlite3
import time

# 字符串子序列匹配
def match_sub(a,b):
    length_a = len(a)
    length_b = len(b)
    max_compared = [0] * (length_b + 1)
    for i in range(length_a):
        for j in range(length_b, 0,-1):
            if b[j-1] == a[i]:
                max_compared[j] = max_compared[j-1] + 1
        
        for j in range(length_b):
            max_compared[j+1] = max(max_compared[j+1], max_compared[j])
    
    return max_compared[length_b]


#我们所期望的一条信息包含的内容
class Infomation:
    def __init__(self, tid, college, major, name, page, visitor, directions):
        self.tid = tid
        self.college = college
        self.major = major
        self.name = name
        self.page = page
        self.visitor = visitor
        self.directions = directions
    
    # 查询时，与老师信息的匹配度
    # 只要看college，major，name，directions
    # 由于还没分类，所以一起匹配了
    def compare(self,request_info):
        length = len(request_info)
        max_result = 0
        max_result = max(max_result, match_sub(self.college, request_info))
        max_result = max(max_result, match_sub(self.major, request_info))
        max_result = max(max_result, match_sub(self.name, request_info))
        max_result = max(max_result, match_sub(self.directions, request_info))
        return max_result
    

class Spider:
    #直接获取目标url的内容
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
        }
        self.url = url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/55.0.2883.87 Safari/537.36'}
        self.r = requests.get(url, headers = headers)
        self.soup = BeautifulSoup(self.r.text,features='lxml')
        self.teachers = []

    #从报文中获取学院，专业，名字，个人主页信息
    def getinfo(self, dbname = None):
        major = None
        college = None
        name = None
        page = None
        tid = 0
        self.teachers = []
        self.features = {}
        if dbname != None:
            conn = sqlite3.connect(dbname + '.db')
        for ul in self.soup.find_all("td"):
            # 判断是不是描述学院信息的
            if ul.get("colspan")=="5":
                college = ul.string
                #if college == "物理学院":
                #    break
                print(college)
            
            # 判断是不是描述专业信息的
            # 因为和专业编号冲突，只能通过选择最靠近导师信息的作为专业信息
            elif ul.get("rowspan")==None and ul.get("style") == None and ul.get("align") == None:
                major = ul.string
            
            # 判断是不是描述导师个人信息的
            # name为导师名字 page为导师主页 tid作为导师编号
            elif ul.string== None and ul.p != None and college != None and major != None:

                # 那么逐条查询导师信息
                for adviser in ul.find_all('a'):
                    name = adviser.string
                    page = adviser.get("href")
                    # 用网页链接去重
                    if self.features.get(page):
                        continue
                    tid = tid + 1
                    self.features[str(page)] = tid

                    # 如果有数据库就直接查询
                    if dbname != None:
                        c = conn.cursor()
                        data = c.execute("SELECT visitor,directions FROM TEACHER WHERE page=?",(page,))
                        for record in data : 
                            visitor = record[0]
                            directions = record[1]
                    else :
                        # 访问导师主页 
                        # visitor访问量和 direction研究方向
                        personal_page = Spider(page)

                        # visitor访问量
                        # # 从字符串中提取访问量数字
                        # 有时候会乱码，乱码就跳过了
                        visitor_num = personal_page.soup.find("td",width="365",align="left")
                        try:
                            visitor=int(visitor_num.text[8:])
                        except ValueError:
                            continue
                        except AttributeError:
                            continue

                        # direction研究方向
                        table_num = 0
                        directions = ""
                        for reserch in personal_page.soup.find_all("table",width="950"):
                            table_num = table_num + 1
                            #根据网页的框架，第5个table中是研究方向
                            if table_num == 5 :
                                for direction in reserch.find_all("div"):
                                    directions = directions + " \n" + direction.string
                        
                    # 将导师信息放入列表
                    info = Infomation(tid, college, major, name, page, visitor, directions)
                    self.teachers.append(info)

        if dbname != None :
            conn.close()

    #构建数据库 change为是否重建数据库
    def initdb(self, dbname, change = False):
        self.database = dbname

        #在dbname.txt中存储时间，实现每隔一天更新一次数据库
        fp = open(dbname + '.txt', 'r+')
        nowtime = float(time.time())
        lasttime = fp.read()
        if lasttime == "":
            change = True
        else :
            lasttime = float(lasttime)
        print("lasttime: ",lasttime)
        print("nowtime: ",nowtime)
        if change == False and nowtime - lasttime > 86400 :
            change = True
        
        if change :
            self.deletedb(dbname)
            fp.write(str(nowtime))
        fp.close()
        conn = sqlite3.connect(dbname + '.db')
        print("Opened database successfully")
        c = conn.cursor()
        # 如数据库不存在，就创建数据库
        if change or not c.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='TEACHER'").fetchall():
            print("Database is None")
            self.getinfo()
            c.execute('''CREATE TABLE TEACHER
                (ID INTEGER PRIMARY KEY     AUTOINCREMENT,
                PAGE            TEXT   NOT NULL,
                VISITOR        INTEGER    NOT NULL,
                DIRECTIONS     TEXT       NOT NULL);
                ''')
            
            print("TEACHER Table Created!")
            for info in self.teachers:
                c.execute("INSERT INTO TEACHER (PAGE,VISITOR,DIRECTIONS) \
                VALUES (?,?,?)",(info.page, info.visitor, info.directions))
        else:
            print("Database is exist")
            self.getinfo(dbname)
        conn.commit()
        conn.close()

    # 删除数据库
    def deletedb(self, dbname):
        conn = sqlite3.connect(dbname + '.db')
        print("Opened database successfully")
        c = conn.cursor()
        if c.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='TEACHER'").fetchall():
            c.execute("DROP TABLE TEACHER")
        conn.commit()
        conn.close()
        print("Table deleted successfully")
    
    # 展示数据库
    def showdb(self, dbname):
        conn = sqlite3.connect(dbname + '.db')
        print("Opened database successfully")
        c = conn.cursor()
        data = c.execute("SELECT page,visitor,directions FROM TEACHER")
        for info in data:
            print("page = ", info[0])
            print("visitor = ", info[1])
            print("directions = ", info[2], "\n")
        print("Operation done successfully")
        conn.close()

if __name__ == "__main__":
    content = Spider('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023')
    content.initdb('../database/teacher')
    #content.showdb('../database/teacher.db')


