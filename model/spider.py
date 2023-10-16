import requests 
from bs4 import BeautifulSoup
import json
import sqlite3

# 字符串子序列匹配
def match_sub(a,b):
    length_a = len(a)
    length_b = len(b)
    max_compared = [0] * (length_b + 1)
    for i in range(length_a):
        for j in range(length_b, 0,-1):
            if b[j-1] == a[i-1]:
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
        self.direcions = directions
    
    # 查询时，与老师信息的匹配度
    # 只要看college，major，name，directions
    # 由于还没分类，所以一起匹配了
    def compare(self,request_info):
        length = len(request_info)
        max_result = 0
        max_result = max(max_result, match_sub(self.college, request_info))
        max_result = max(max_result, match_sub(self.major, request_info))
        max_result = max(max_result, match_sub(self.name, request_info))
        max_result = max(max_result, match_sub(self.direcions, request_info))
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
    def getinfo(self):
        major = None
        college = None
        name = None
        page = None
        tid = 0
        for ul in self.soup.find_all("td"):

            # 判断是不是描述学院信息的
            if ul.get("colspan")=="5":
                college = ul.string
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
                    tid=tid+1
                    name = adviser.string
                    page = adviser.get("href")

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
                                directions = directions + direction.string
                    
                    # 将导师信息放入列表
                    info = Infomation(tid, college, major, name, page, visitor, directions)
                    self.teachers.append(info)

if __name__ == "__main__":

    content = Spider('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023')
    content.getinfo()

