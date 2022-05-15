from flask import request,url_for,render_template,redirect,session,abort,flash,Blueprint
from flask_sqlalchemy import SQLAlchemy
import os
import random
import string
HOST = '127.0.0.1:5000'
#HOST = 'https://kapil829.pythonanywhere.com'
app = Blueprint("setting",'settingApp',static_folder='static',template_folder='templates')
db = SQLAlchemy()
def geneate_dict(usr):
    detail = {}
    detail['about'] = usr.about
    detail['facebook'] = usr.facebook
    detail['intro'] = usr.intro
    detail['telephone'] = usr.telephone
    detail['twitter'] = usr.twitter
    detail['instagram'] = usr.instagram
    return detail
def all_subscrber(usr):
    allrecepient_no = list(eval(Subscriber.query.filter_by(user_id = usr.user_id).first().subscribers))
    return User.query.filter(User.user_id.in_(tuple(allrecepient_no))).all()
def all_subscriptn(usr):
    allrecepient_no = list(eval(Subscription.query.filter_by(user_id = usr.user_id).first().subscriptions))
    return User.query.filter(User.user_id.in_(tuple(allrecepient_no))).all()
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
def setting():
    user = None
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        usrdetil = UserDetail.query.filter_by(email=session['user']).first()
        subscriber = Subscriber.query.filter_by(email = session['user']).first()
        subscription = Subscription.query.filter_by(email = session['user']).first()
        no_of_pst = len(Post.query.filter_by(email = session['user']).all())
        return render_template('setting.html',user = user,usrdetail=usrdetil,subscribr = subscriber.no_of_subscrbs,subscrptn = subscription.no_of_subscrptn,no_of_pst = no_of_pst)
    return redirect('/user/login')
@app.route('/change_setting/<string:setting>',methods = ['GET','POST'])
def changeSetting(setting):
    usr = None
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
        usrdetil = UserDetail.query.filter_by(email = session['user']).first()
        if(request.method == "POST"):
            if setting == 'story':
                about = request.form.get('about')
                intro = request.form.get('intro')
                usrdetil.about = about
                usrdetil.intro = intro
                db.session.commit()
            elif setting == 'info':
                name = request.form.get('name')
                tele = request.form.get('tele')
                facebook = request.form.get('facebook')
                twitter = request.form.get('twitter')
                instagram = request.form.get('instagram')
                usr.name = name
                usrdetil.telephone = tele
                usrdetil.facebook = facebook
                usrdetil.twitter = twitter
                usrdetil.instagram = instagram
                db.session.commit()
            flash('Change Successfull')
            return redirect('/user/setting')
        if request.method == 'GET':
            detail = geneate_dict(usrdetil)
            return render_template('changesetting.html',setting = setting,user=usr,detail = detail)
    return abort(404)

@app.route('/<string:option>')
def subscrbr_subscrptn(option):
    if 'user' in session:
        if option == 'subscriber':
            subscrbr = all_subscrber(User.query.filter_by(email=session['user']).first())
            return render_template('subscrbr_subscrptn.html',subscrbr = subscrbr)
        elif option == 'subscription':
            subscrptn = all_subscriptn(User.query.filter_by(email=session['user']).first())
            return render_template('subscrbr_subscrptn.html',subscrptn = subscrptn)
    else:
        return redirect('/user/login')
@app.route('/getlink',methods=['POST','GET'])
def getlink():
    if request.method=='GET':
        return render_template('get_email.html')
    if request.method == 'POST':
        email = request.form.get('email')
        if not User.query.filter_by(email = email).first():
            flash('Wronge Email')
            return redirect('/user/login')
        session['resetdata'] = email
        return redirect('/resetpass')
    return abort(404)
@app.route('/resetpass/',methods = ['POST','GET'])
def resetpass():
    if True:
        usr = User.query.filter_by(email=session['resetdata']).first()
        if usr:
            if request.method == 'GET':
                return render_template('changepass.html',link = link_)
            elif request.method == 'POST':
                newpass = request.form.get('newpass')
                confpass = request.form.get('confpass')
                if newpass ==confpass:
                    usr.password = newpass
                    db.session.commit()
                    email = None
                    session['resetdata'] = email
                    flash('Password Reset')
                    return redirect('/user/login')
    else:
        abort(404)