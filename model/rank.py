import requests 
from bs4 import BeautifulSoup
import json
import sqlite3
from model.spider import Spider
from model.spider import Infomation

class Rank():
    # ranklist为teacher的排序副本
    def __init__(self, url, database):
        spider = Spider(url)
        spider.initdb(database)

        # 使用元组，为了方便排序
        self.ranklist = []
        for info in spider.teachers:
            self.ranklist.append((info.tid, info.college, info.major, info.name, info.page, info.visitor, info.directions))
        
    # info_type 为类型 0-默认 1-学院 2-专业 3-名字 5-访问量
    def rank(self, info_type):
        self.ranklist.sort(key=lambda x:x[info_type],reverse=True)
        return
        
if __name__ == "__main__":
    content = Rank('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', '../database/teacher')
    content.rank(5)
    cs = 0
    for info in content.ranklist:
        cs = cs + 1
        print(info)
        if cs == 100:
            break
