from flask import request,url_for,render_template,redirect,session,abort,flash,Blueprint
from flask_sqlalchemy import SQLAlchemy
import datetime
import smtplib
app = Blueprint("offer",'offerApp',static_folder='static',template_folder='templates')
db = SQLAlchemy()
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
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
        offers = Offers.query.filter_by().all()
        return render_template('offer.html',usr = usr,offers=offers)
    else:
        flash('Please Login First')
        return redirect('/user/login')
@app.route('/addoffer',methods = ['POST','GET'])
def addoffer():
    if 'user' in session:
        usr = User.query.filter_by(email=session['user']).first()
        if usr.admin:
            if request.method == 'GET':
                return render_template('addoffer.html')
            elif request.method == 'POST':
                name = request.form.get('name')
                no_of_post = request.form.get('no_of_post')
                discount = request.form.get('discount')
                price = request.form.get('price')
                offer = Offers(offername = name,no_of_post=no_of_post,price = price,discount = discount)
                db.session.add(offer)
                db.session.commit()
                flash('offer added')
                return redirect('/dashboard')
        else:
            abort(404)
    else:
        abort(404)
@app.route('/delete-offer/<int:sno>')
def delete_offer(sno):
    if not 'user' in session:
        return abort(404)
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        if user.admin:
            Offers.query.filter_by(offer_id = sno).delete()
            db.session.commit()
            flash('Offer Deleted Successfully')
    return redirect('/dashboard')
@app.route('/editoffer',methods = ['GET'])
def editoffer():
    user = None
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
    if request.method == 'GET' and user:
        offer_id = request.args.get('offer_id',-1)
        if offer_id != -1:
            offer = Offers.query.filter_by(offer_id = offer_id).first()
            if offer:
                return render_template('addoffer.html',offer = offer,user = user)
            else:
                return render_template('addoffer.html',user = user)
        flash('Something Went Wronge')
        return redirect('/')
    return abort(404)
@app.route('/changeoffer/<int:offer_id>',methods = ['POST'])
def changeoffer(offer_id):
    if not 'user' in session:
        return abort(404)
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        if user.admin:
            if request.method == 'POST':
                offer = Offers.query.filter_by(offer_id = offer_id).first()
                if offer:
                    name = request.form.get('name')
                    no_of_post = request.form.get('no_of_post')
                    discount = request.form.get('discount')
                    price = request.form.get('price')
                    offer.offername = name
                    offer.no_of_post = no_of_post
                    offer.price = price
                    offer.discount = discount
                    db.session.commit()
                    flash('Offer has been Edited')
                    return redirect('/dashboard')
    return abort(404)