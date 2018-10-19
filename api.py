from flask import Flask, jsonify
import pymongo
from config import *
app = Flask(__name__)

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

app.config['JSON_AS_ASCII'] = False   #设置ascii码为False，方便打印中文


@app.route('/',methods=['GET','POST'])
def hello_world():
    return 'please input article_list page or article_detail id or article_message title'

# 使用同一个视图函数
# <>定义路由参数 <>内需要起个名字
# 通过文章页数返回文章列表
@app.route('/article_list/<int:page>',methods = ['GET','POST'])
def get_article_list(page):
    # if request.method == 'POST':
    start = 10 * (page - 1)   # 每十条数据为一页，计算该page起点为第几条数据
    my_list = []                # 保存数据库中获得的数据
    for list in db['ithome'].find({}, {"_id:": 1, "title": 1, "date": 1}).sort('date', -1).skip(start).limit(10):
        # print(list)
        my_list.append(list)
    data = {'data': my_list}     #打包数据并返回json格式的data
    # print(data)
    return jsonify(data)

#通过文字id返回文章的信息
@app.route('/article_detail/<int:id>',methods=['GET','POST'])
def get_article_detail(id):
    data = db['ithome'].find_one({"_id":id},{"_id":0})
    # print(data)
    return jsonify(data)

#通过文章的标题返回文章的信息
@app.route('/article_message/<string:title>',methods=['GET','POST'])
def get_article_message(title):
    data = db['ithome'].find_one({"title":title})
    # print(data)
    return jsonify(data)
if __name__ == '__main__':
    app.run()
