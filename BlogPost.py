from flask import Flask,jsonify,request
from flask.views import MethodView
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


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
        content=request.json['content']
        if username is None:
            username="Anonymous"
        query=users.find_one({'username':username})
        if query:
            blog_post=everything.insert({'username':query['username'],'content':content})
            blog_add_check=everything.find_one({'_id': blog_post})
            query['posts'].append({"id":blog_post.get('insertedId')})
            if blog_add_check:
                user_id=users.update({'username': username}, {'username': query['username'],'email': query['email'],'password': query['password'],'posts': query['posts']})
                return jsonify({"message":"Post Posted as "+username,"code":"201"}),201
            else:
                return jsonify({"message":"Post cannot be added"})
        else:
            return jsonify({"message":"No user with this username"})

        
    def delete(self):
        post_id=request.json['post_id']
        if post_id is None:
            return jsonify({"message":"Post deletion failed. Please Specify a postid","code":"204"}),204
        else:
            post=everything.find_one({'_id':ObjectId(post_id)})
            if post:
                username=post['username']
                user_profile=users.find_one({'username':username})
                dpost=everything.remove({'_id':  ObjectId(post_id)})
                #user_profile['posts'].remove({"$oid": post_id})
                user_profile['posts'] = [i for i in user_profile['posts'] if i.get('$oid') != post_id]
                user_id=users.update({'username': username}, {'username': user_profile['username'],'email': user_profile['email'],'password': user_profile['password'],'posts': user_profile['posts']})
                return jsonify({"message":"Post deleted succesfully"})                    
            else:
                return jsonify({"Message":"No post with this post id exists"})
                


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
                 

@app.route('/getusers',methods=['GET'])
def find_all_user():
    result=[]
    for item in users.find():
        stri=item["username"]
        #stri=stri.encode('ascii')
        result.append(stri)
    return jsonify({"usernames":result})

@app.route('/login',methods=['POST'])
def find_pass():
    email=request.json['email']
    password=request.json['password']
    if email is None or password is None:
        return jsonify({"message":"Bad Request","code":"400"}),400
    else:
        query=users.find_one({'email': email})
        if query:
            result={'email':query['email'],'password':query['password']}
            if result['password']==password:
                return jsonify({"message":"Login succesful","code":"200"}),200
            else:
                return jsonify({"message":"Unauthorized Access","code":"401"}),401
        else:
            return jsonify({"message":"No account with this email","code":"404"}),404

@app.route('/join',methods=['POST'])
def create_acc():
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']
    user_email_exist_check=users.find_one({'email': email})
    user_username_exist_check=users.find_one({'username': username})
    if user_email_exist_check or user_username_exist_check:
        return jsonify({"message":"Username or Email already exist","code":"409"}),409
    else:
        user_id=users.insert({'username':username,'email':email,'password':password,"posts":[]})
        user_add_check=users.find_one({'_id': user_id})
        if user_add_check:
            return jsonify({"message":"User added succesfully","code":"201"}),201
        else:
            return jsonify({"message":"User cannot added due to internal error","code":"500"}),500

if(__name__)=='__main__':
    app.run(host='0.0.0.0',debug=True)

