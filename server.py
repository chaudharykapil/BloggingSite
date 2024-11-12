from flask import Flask,request,url_for,render_template,redirect,session,abort,flash,send_from_directory
import math,os,random
from post.init import app as postapp
from offer.init import app as offerapp
from user.init import app as userapp
from user.user_setting.init import app as settingapp
from utils.DBManager import db,Offers,Post,Subscriber,Subscription,User,UserDetail,UserVote
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SECRET_KEY'] = '#youcantgowithouthackthis12129090883434####'
db.init_app(app=app)
app.register_blueprint(postapp,url_prefix = '/post')
app.register_blueprint(userapp,url_prefix = '/user')
app.register_blueprint(settingapp,url_prefix = '/user/setting')
app.register_blueprint(offerapp,url_prefix = '/offer')


app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static\\profile_pic')
def deletepic(filename):
    try:
        os.remove(app.config['UPLOAD_FOLDER']+'\\'+filename)
        return True
    except:
        return False
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)