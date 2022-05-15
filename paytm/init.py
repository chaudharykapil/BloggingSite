from flask import request,render_template,redirect,session,abort,Blueprint,flash
from flask_sqlalchemy import SQLAlchemy
import smtplib
from  payTm import Checksum
import random
import math
app = Blueprint("paytmapi",'userApp',static_folder='static',template_folder='templates')
db = SQLAlchemy()
def send_email(to,message):
    try:
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.starttls()
        s.login('rs405384@gmail.com','khushi8279')
        s.sendmail('rs405384@gmail.com',to,message)
        return True
    except:
        send_email(to,message)
MERCHENT_KEY = '_c_ST&Fa7u5ssCAY'
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
@app.route('/',methods=['POST'])
def paytmrequest():
    
    global offer
    if 'user' in session:
        if request.method == 'POST':
            offer = Offers.query.filter_by(offer_id = request.form.get('offer_id')).first()
            acc_detl = {
            'MID':'AcLOpt14505058891585',
            'ORDER_ID':str(random.randint(1,100000)),
            'TXN_AMOUNT':str(offer.price-((offer.discount/100)*offer.price)),
            'CUST_ID':session['user'],
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:5000/pay/response/',
            #'CALLBACK_URL':'https://securegw-stage.paytm.in/order/status',
            }
            param = acc_detl
            param['CHECKSUMHASH']=Checksum.generate_checksum(acc_detl,MERCHENT_KEY)
            return render_template('paytmrequest.html',offer = offer,acc_detl=param)
        else:
            abort(404)
    else:
        abort(404)
@app.route('/response/',methods=['POST'])
def response():
    
    global offer
    resp_dict = {}
    form = request.form
    for i in form.keys():
        resp_dict[i]=form[i]
    if 'CHECKSUMHASH' in resp_dict:
        checksum = resp_dict['CHECKSUMHASH']
    verify = Checksum.verify_checksum(resp_dict,MERCHENT_KEY,str(checksum))
    if verify:
        if resp_dict['RESPCODE'] == '01':
            usr =User.query.filter_by(email = session['user']).first()
            if usr.available_post != -1:
                usr.available_post += offer.no_of_post
                db.session.commit()
            offer = None
            flash('Order Successful')
            return redirect('/')
    return 'Payment unsuccessful due to '+ str(resp_dict['RESPMSG'])