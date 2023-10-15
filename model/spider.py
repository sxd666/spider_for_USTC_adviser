import requests 
from bs4 import BeautifulSoup
import time
import json
import sqlite3

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
        #print(self.r.text)
        self.soup = BeautifulSoup(self.r.text)

if __name__ == "__main__":

    content = Spider('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023')
    