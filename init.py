from flask import Flask,request,url_for,render_template,redirect,session,abort,flash,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import math,os,random
from post.init import app as postapp,postdb
from offer.init import app as offerapp,db as offerdb
from user.init import app as userapp,db as userdb 
from user.user_setting.init import app as settingapp,db as settingdb
#from paytm.init import app as paytmapp,db as paytmdb
DATABASE_NAME = 'root'
DATABASE_PASS = 'kapil'
HOST = 'localhost'
#HOST = 'kapil829.pythonanywhere.com'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'+DATABASE_NAME+':'+DATABASE_PASS+'@'+HOST+'/final_blog'

app.config['SECRET_KEY'] = '#youcantgowithouthackthis12129090883434####'
db = SQLAlchemy(app)
app.register_blueprint(postapp,url_prefix = '/post')
postdb.__init__(app)
app.register_blueprint(userapp,url_prefix = '/user')
userdb.__init__(app)
app.register_blueprint(settingapp,url_prefix = '/user/setting')
settingdb.__init__(app)
app.register_blueprint(offerapp,url_prefix = '/offer')
offerdb.__init__(app)
#app.register_blueprint(paytmapp,url_prefix = '/pay')
#paytmdb.__init__(app)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static\\profile_pic')
def deletepic(filename):
    try:
        os.remove(app.config['UPLOAD_FOLDER']+'\\'+filename)
        return True
    except:
        return False
class Post(db.Model):
    __tablename__ = "post"
    sno = db.Column(db.Integer,primary_key = True,nullable = False)
    title = db.Column(db.String(100),nullable = False)
    subtitle = db.Column(db.String(50),nullable = True)
    content = db.Column(db.Text())
    email = db.Column(db.String(30),nullable = False)
    dt = db.Column(db.String(30),nullable = True)
    post_link = db.Column(db.String(100),nullable = False)
    user = db.Column(db.String(50))
    total_vote = db.Column(db.Integer,nullable = False)
    suspend = db.Column(db.Boolean(),nullable = False)
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer,primary_key = True,nullable = False)
    name = db.Column(db.String(30),nullable = False)
    email = db.Column(db.String(30),nullable = False)
    password = db.Column(db.String(100),nullable = False)
    admin = db.Column(db.Boolean,nullable = False)
    profile_pic = db.Column(db.String(100),nullable = False)
    available_post = db.Column(db.Integer,nullable = False)
class UserDetail(db.Model):
    __tablename__ = 'userdetail'
    email = db.Column(db.String(30),nullable = False,primary_key=True)
    about = db.Column(db.Text())
    intro = db.Column(db.Text())
    telephone = db.Column(db.Text())
    facebook = db.Column(db.Text())
    instagram = db.Column(db.Text())
    twitter = db.Column(db.Text())
class UserVote(db.Model):
    __tablename__ = 'uservote'
    user_id = db.Column(db.Integer,primary_key = True,nullable = False)
    email = db.Column(db.String(30),nullable = False)
    upvote_post = db.Column(db.Text())
class Subscriber(db.Model):
    '''
    #subscriber handle all the user which subscribe that channel
    '''
    __tablename__ = 'subscriber'
    user_id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(30),nullable = False)
    no_of_subscrbs = db.Column(db.Integer,nullable = False)
    subscribers = db.Column(db.Text())
class Subscription(db.Model):
    '''
    #subscription handle all the channel which has been subscribed by user
    '''
    __tablename__ = 'subscription'
    user_id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(30),nullable = False)
    no_of_subscrptn = db.Column(db.Integer,nullable = False)
    subscriptions = db.Column(db.Text())
class Offers(db.Model):
    __tablename__='offer'
    offer_id = db.Column(db.Integer,primary_key=True)
    offername = db.Column(db.Text())
    no_of_post = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Integer,nullable=False)
    discount = db.Column(db.Float)
@app.route('/')
def home():
    no_of_post = 4
    usr = None
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
    posts = Post.query.filter_by(suspend = False).all()
    posts.reverse()
    totlpage = math.ceil(len(posts)/no_of_post)
    # request.args.get(key) function used to get value 
    # from url which is in form of /?key = 'some value'
    page = request.args.get('page','')
    if(not page.isnumeric()):
        page = 0
    else:
        page = int(page)
    posts = posts[page*no_of_post:(page+1)*no_of_post]
    if page == 0 and len(posts)>no_of_post:
        nextpg = str(page+1)
        prev = '#'
    elif page == totlpage-1:
        nextpg = totlpage-1
        if page == 0:
            prev = '0'
        else:
            prev = str(page-1)
    else:
        nextpg = str(page+1)
        prev = str(page-1)
    return render_template('index.html',posts = posts,user = usr,next = nextpg,prev = prev)
@app.route('/contact')
def contact():
    usr = None
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
    return render_template('contact.html',user = usr)
@app.route('/about')
def about():
    usr = None
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
    return render_template('about.html',user = usr)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        if user.admin:
            post = Post.query.filter_by().all()
            post.reverse()
            offers=Offers.query.filter_by().all()
            return render_template('dashboard.html',post = post,user = user,offers=offers)
    return abort(404)
@app.route("/upload",methods=['POST'])
def changePic():
    if 'user' not in session:
        return abort(404)
    elif 'user' in session:
        user = User.query.filter_by(email=session['user']).first()
        if user:
            pic = request.files['profile_pic']
            ext = str(pic.filename).split('.')[-1]
            if ext.casefold() != 'jpg'.casefold() and ext.casefold() != 'png'.casefold() and ext.casefold() != 'jpeg'.casefold():
                return 'Wronge File'
            if user.profile_pic != 'unknown_profile_pic.jpg':
                deletepic(user.profile_pic)
            picname = user.name+'_profile_pic'+str(random.randint(0,100))+'.jpg'
            pic.save(app.config['UPLOAD_FOLDER']+'\\'+picname)
            user.profile_pic = picname
            db.session.commit()
            return redirect('/user/setting')
    return abort(404)
@app.route('/uploadfolder/<filename>')
def uploadfolder(filename):
    if 'user' in session:
        return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
    return abort(404)
if __name__ == "__main__":
    
    app.run(debug=True)