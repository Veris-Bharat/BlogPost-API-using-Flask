from flask import Flask,render_template,request,session,redirect,url_for,jsonify
import os
from flask_login import LoginManager,UserMixin
from flask.views import MethodView
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app=Flask(__name__)
app.config.from_object('config')
#login_manager=LoginManager()
#login_manager.init_app(app)

mongo=PyMongo(app)
users=mongo.db.Users
tokens=mongo.db.Token
blogs=mongo.db.Blogs

class UserAPI(MethodView):
    def get(self,username,pid=None):
        token_id=tokens.find_one({'username':username})
        token=request.headers['token']
        if token==token_id['token']:
            if pid==None:
                result=[]
                for blogpost in blogs.find():
                    result.append(blogpost)
                return str(result)
            else:
                result=[]
                blog=blogs.find_one({"_id":ObjectId(pid)})
                result.append(blog)
                return str(result)
        else:
            return jsonify({"message":"User Authentication failed","code":"401"}),401
        
    def post(self,username):
        content=request.json['content']
        token_id=tokens.find_one({'username':username})
        if token_id is None:
            return jsonify({"message":"No user with this username","code":"204"}),204
        token=request.headers.get('token')
        if token==token_id['token']:
            blog_post=blogs.insert({'author':username,'content':content})
            blog_add_check=blogs.find_one({'_id': blog_post})
            if blog_add_check:
                return jsonify({"message":"Post Posted as "+username,"code":"201"}),201
            else:
                return jsonify({"message":"Post cannot be added",'code':'502'}),502
        else:
            return jsonify({"message":"User Authentication failed","code":"401"}),401
 
    def delete(self,username,pid=None):
        if pid is None:
            return jsonify({"message":"Post deletion failed. Please Specify a postid","code":"204"}),204
        else:
            token_id=tokens.find_one({'username':username})
            token=request.headers['token']
            if token==token_id['token']:
                post_id=blogs.find_one({'_id':ObjectId(pid)})
                if post_id:
                    if post_id['author']==username:
                        dpost=blogs.remove({'_id':ObjectId(pid)})
                        return jsonify({"message":"Post deleted succesfully",'code':'200'}),200
                    else:
                        return jsonify({"message":"not your post. you can't delete it","code":"401"}),401
                else:
                    return jsonify({"Message":"No post with this post id","code":"204"}),204
            else:
                return jsonify({"message":"User authentication failed","code":"401"}),401

    def put(self,username,pid=None):
        content=request.json['content']
        if pid is None:
            return jsonify({"Message":"Please enter a post_id","code":"204"}),204
        else:
            token_id=tokens.find_one({'username':username})
            token=request.headers['token']
            if token==token_id['token']:
                query=blogs.find_one({'_id':ObjectId(pid)})
                if query:
                    if query['author']==username:
                        post_id=blogs.update({'_id': ObjectId(pid)},{'author':username,'content':content})
                        if post_id:
                            return jsonify({"message":"Post updated succesfully",'code':'200'}),200
                        return "error"
                    else:
                        return jsonify({"message":"not your post. you can't edit it","code":"401"}),401
                else:
                    return jsonify({"message":"No post with this post id","code":"204"}),204
            else:
                return jsonify({"message":"User authentication failed","code":"401"}),401

user_view=UserAPI.as_view('user_api')
app.add_url_rule('/api/v2/user/<username>/blogs',view_func=user_view,methods=['GET','POST'])
app.add_url_rule('/api/v2/user/<username>/blogs/<pid>',view_func=user_view,methods=['GET','DELETE','PUT'])



"""@app.route('/api/v2/')
def index():
    if 'username' in session:
        username =session['username']
        return 'Logged in as '+username+"<br><b><a href = '/api/v2/logout'>click here to log out</a></b>"
        #return redirect(url_for('dashboard',user=username))
    return render_template('index.html')
"""

@app.route('/api/v2/login',methods=['POST'])
def login():
    username=request.json['username']
    password=request.json['password']
    if email is None or password is None:
        return jsonify({"message":"Bad Request","code":"400"}),400
    user_check=users.find_one({'username':username})
    if user_check:
        if user_check['password']==password:
            #session['username']=username
            #return redirect(url_for('index'))
            token_id=tokens.find_one({'username':username})
            return jsonify({'message':'login succesfull','code':'200','token':token_id['token']}),200
        else:
            return jsonify({"message":"Unauthorized Access","code":"401"}),401
    else:
        return jsonify({"message":"No account with this email","code":"404"}),404
   
@app.route('/api/v2/register',methods=['POST'])
def register():
    username=request.json['username']
    email=request.json['email']
    existing_email=users.find_one({'email': email})
    existing_username=users.find_one({'username': username})
    if existing_email is None and existing_username is None:
        user_id=users.insert({'username':username,'email':email,'password':request.json['password']})
        token_id=tokens.insert({'username':username,'token':os.urandom(6).encode('hex')})
        #session['username']=request.form['username']
        #return redirect(url_for('index'))
        return jsonify({'message':'user created','code':'202'}),202
    else:
        return jsonify({"message":"Username or Email already exist","code":"409"}),409
    #return render_template('register.html')


if(__name__)=='__main__':
    app.run()
