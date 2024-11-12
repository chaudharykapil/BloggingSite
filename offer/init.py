from flask import request,url_for,render_template,redirect,session,abort,flash,Blueprint
from utils.DBManager import db,Offers,Post,Subscriber,Subscription,User,UserDetail,UserVote
app = Blueprint("offer",'offerApp',static_folder='static',template_folder='templates')
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