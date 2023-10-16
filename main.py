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

@app.route('/search')
def search():
    # get the keyword from the POST
    if request.method == 'POST':
        return render_template('search.html')
    else:
        return render_template('search.html')
@app.route('/rank_tid')
def rank_tid():
    return render_template('rank.html')
@app.route('/rank_college')
def rank_college():
    return render_template('rank.html')
@app.route('/rank_major')
def rank_major():
    return render_template('rank.html')
@app.route('/rank_name')
def rank_name():
    return render_template('rank.html')
@app.route('/rank_visitor')
def rank_visitor():
    return render_template('rank.html')

if __name__ == '__main__':
    app.run(port=5009,debug=True) 