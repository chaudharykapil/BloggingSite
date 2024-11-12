from flask import request,url_for,render_template,redirect,session,abort,flash,Blueprint
from utils.DBManager import db,Offers,Post,Subscriber,Subscription,User,UserDetail,UserVote
app = Blueprint("setting",'settingApp',static_folder='static',template_folder='templates')
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
                return render_template('changepass.html')
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