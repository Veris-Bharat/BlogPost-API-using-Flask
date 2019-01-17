from flask import Flask,jsonify,request
from flask.views import MethodView
from flask_pymongo import PyMongo

app=Flask(__name__)

app.config['MONGO_DBNAME']='people'
app.config['MONGO_URI']='mongodb://bharat:bharat123@ds157864.mlab.com:57864/people'

mongo=PyMongo(app)
users=mongo.db.Users
everything=mongo.db.everything

class UserAPI(MethodView):
    def get(self,ids):
        if ids is None:
            #return everything
            pass
        else:
            #return posts by username
            pass
    def post(self):
        username=request.json['username']
        if username is None:
            #post as anonymous
            content=request.json['content']
            blog_post=everything.insert({'username':"anonymous",'content':content})
            blog_add_check=everything.find_one({'_id': blog_post})
            if blog_add_check:
                return jsonify({"message":"Posted as anonymous","code":"201"}),201
            else:
                return jsonify({"message":"Post cannot be added"})
        else:
            #post as username
            content=request.json['content']
            query=users.find_one({'username': username})
            if query:
                blog_post=everything.insert({'username':query['username'],'content':content})
                blog_add_check=everything.find_one({'_id': blog_post})
                if blog_add_check:
                    user_id=users.update({'username': username}, {'posts': 'posts.append(blog_post)'})
                    return jsonify({"message":"Post Posted","code":"201"}),201
                else:
                    return jsonify({"message":"Post cannot be added"})
            else:
                return jsonify({"message":"No user with this username"})
        
    def delete(self,ids):
        if ids is None:
            return jsonify({"message":"Post deletion failed. Please Specify a postid","code":"204"}),204
        else:
            #delete post
            pass
    def put(self,ids):
        if ids is None:
            return jsonify({"message":"Post updation failed. Please provide a postid","code":"204"}),204
        else:
            #update post
            pass

user_view=UserAPI.as_view('user_api')
app.add_url_rule('/dashboard',view_func=user_view,methods=['GET','POST','DELETE','PUT'])
#app.add_url_rule('/dashboard',defaults={'ids':None},view_func=user_view,methods=['GET','POST','DELETE','PUT'])
#app.add_url_rule('/dashboard/<ids>',view_func=user_view,methods=['GET','POST','DELETE','PUT'])
                 

@app.route('/',methods=['POST'])
def find_pass():
    username=request.json['username']
    password=request.json['password']
    query=users.find_one({'username': username})
    if query:
        result={'username':query['username'],'password':query['password']}
        if result['password']==password:
            return jsonify({"message":"Login succesful",
                        "code":"202"}),202
        else:
            return jsonify({"message":"incorrect password","code":"204"}),204
    else:
        return jsonify({"message":"No account with this username"})

@app.route('/join',methods=['POST'])
def create_acc():
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']

    user_id=users.insert({'username':username,'email':email,'password':password,"posts":[]})
    user_add_check=users.find_one({'_id': user_id})
    if user_add_check:
        return jsonify({"message":"User added succesfully",
                        "code":"201"}),201
    else:
        return jsonify({"message":"User cannot added"})

if(__name__)=='__main__':
    app.run(debug=True)

