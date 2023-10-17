# 利用flask构建前端界面
from flask import Flask, request
from flask import render_template
from model.search import Search  
from model.rank import Rank

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/index')
def home():
    return index()
#搜索匹配度前100的信息，并输出
@app.route('/search',methods = ['GET', 'POST'])
def search():
    if request.method == 'POST':
        message = request.form.get('search')
        result = Search('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', 'database/teacher')
        result.rank(message)
        ranklist = []
        number = 0
        for info in result.ranklist:
            ranklist.append(info[2])
            number = number + 1
            if number == 100 : 
                break
        return render_template('search.html', teacherlist = ranklist)
    else:
        return render_template('search.html')
#按默认排序
@app.route('/rank_tid')
def rank_tid():
    result = Rank('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', 'database/teacher')
    result.rank(0)
    return render_template('rank.html', ranklist = result.ranklist)
#按学院排序
@app.route('/rank_college')
def rank_college():
    result = Rank('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', 'database/teacher')
    result.rank(1)
    return render_template('rank.html', ranklist = result.ranklist)
#按专业排序
@app.route('/rank_major')
def rank_major():
    result = Rank('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', 'database/teacher')
    result.rank(2)
    return render_template('rank.html', ranklist = result.ranklist)
#按名字排序
@app.route('/rank_name')
def rank_name():
    result = Rank('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', 'database/teacher')
    result.rank(3)
    return render_template('rank.html', ranklist = result.ranklist)
#按访问量排序
@app.route('/rank_visitor')
def rank_visitor():
    result = Rank('https://dslx.ustc.edu.cn/?menu=expertlist&year=2023', 'database/teacher')
    result.rank(5)
    return render_template('rank.html', ranklist = result.ranklist)

if __name__ == '__main__':
    app.run(port=5009,debug=True) 