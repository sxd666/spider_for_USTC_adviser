import requests 
from bs4 import BeautifulSoup
import json
import sqlite3
from model.spider import Spider
from model.spider import Infomation

class Search():
    # ranklist为teacher的副本
    def __init__(self, url, database):
        spider = Spider(url)
        spider.initdb(database)
        self.searchlist = []
        self.ranklist = []
        for info in spider.teachers:
            self.searchlist.append(info)
        
    # 根据与查询字段的匹配度为主，访问量为辅，进行排序，
    def rank(self, request_info):
        self.ranklist = []
        for info in self.searchlist:
            self.ranklist.append((info.compare(request_info), info.visitor, info))
        self.ranklist.sort(key = lambda x:(-x[0], -x[1]))
        return
        
if __name__ == "__main__":
    content = Search('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', '../database/teacher.db')
    content.rank('人工智能')
    cs = 0
    for info in content.ranklist:
        cs = cs + 1
        print(info[2].name,info[2].college,info[2].directions,info[2].visitor)
        if cs == 10:
            break
