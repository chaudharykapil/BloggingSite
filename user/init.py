from flask import request,url_for,render_template,redirect,session,abort,flash,Blueprint

from utils.DBManager import db,Offers,Post,Subscriber,Subscription,User,UserDetail,UserVote

app = Blueprint("user",'userApp',static_folder='static',template_folder='templates')


@app.route('/register',methods = ['POST','GET'])
def register():
    if(request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')
        if Post.query.filter_by(email = email).first() != None:
            message = 'Username already exist'
            return render_template('register.html',message = message)
        if(pass1 != pass2):
            message = 'Password Do not Match !'
            return render_template('register.html',message = message)
        if(pass1 == pass2 and name != '' and email != '' and ('@' in email)):
            pic = 'profile_pic/unknown_profile_pic.jpg'
            usr = User(name = name,email = email,password = pass1 ,admin = False,profile_pic = pic,available_post = -1)
            db.session.add(usr)
            usr = User.query.filter_by(email = email).first()
            subscriber = Subscriber(user_id=usr.user_id,email = email,no_of_subscrbs = 0,subscribers = '[]')
            db.session.add(subscriber)
            subscription = Subscription(user_id=usr.user_id,email = email,no_of_subscrptn = 0,subscriptions = '[]')
            db.session.add(subscription)
            usrdetil = UserDetail(email = email,about='',facebook='',twitter='',instagram='',intro='',telephone='')
            db.session.add(usrdetil)
            db.session.commit()
            flash('Registered Susscefully')
            return redirect('/user/login')
    return render_template('register.html')
@app.route('/login' , methods = ['POST',"GET"])
def login():
    usr = None
    if request.method == 'POST':
        email = request.form.get('username')
        passw = request.form.get('pass')
        #used to take value of checkbox from html
        remb = request.form.getlist('remember-me')
        if(passw != ''):
            usr = User.query.filter_by(email = email).first()
            if(usr):
                if(passw == usr.password):
                    session['user'] = email
                    if remb:
                        if remb[0] == 'yes':
                            session.permanent = True
                    else:
                        session.permanent = False
                    flash('Login Successfully')
                    return redirect('/')
                else:
                    flash('Incorrect username or password')
                    return redirect('user/login')
            else:
                flash('Incorrect username or password')
                return redirect('user/login')
    return render_template('login.html')
@app.route('/logout')
def logout():
    try:
        session.pop('user')
        flash('Logout Successfully')
    except:
        flash('Allready Logout')
    return redirect('/')
@app.route('/<string:post_link>/<string:username>')
def addsubcriber(post_link,username):
    #subscription handle all the channel which has been subscribed by user
    #subscriber handle all the user which subscribe that channel
    if not 'user' in session:
        return redirect('/user/login')
    elif 'user' in session:
        #subscpt is a person who subscribe the channel or who logged in
        subscpt = Subscription.query.filter_by(email = session['user']).first()
        #real_subscriber is a person who channel has been subscribed
        real_subscriber = Post.query.filter_by(post_link = post_link).first()
        subscbr = Subscriber.query.filter_by(email = username).first()
        if real_subscriber.email == username and not session['user'] == real_subscriber.email:
            if not is_subscribed(subscpt,subscbr):
                all_subscription = list(eval(subscpt.subscriptions))
                all_subscription.append(subscbr.user_id)
                subscpt.no_of_subscrptn = len(all_subscription)
                subscpt.subscriptions = str(all_subscription)
                all_subscriber = list(eval(subscbr.subscribers))
                all_subscriber.append(subscpt.user_id)
                subscbr.no_of_subscrbs = len(all_subscriber)
                subscbr.subscribers = str(all_subscriber)
                db.session.commit()
    return redirect('/post/'+post_link)
@app.route('/<string:post_link>/remove/<string:username>')
def removesubcriber(post_link,username):
    #subscription handle all the channel which has been subscribed by user
    #subscriber handle all the user which subscribe that channel
    if not 'user' in session:
        return redirect('/user/login')
    elif 'user' in session:
        subscpt = Subscription.query.filter_by(email = session['user']).first()
        subscbr = Subscriber.query.filter_by(email = username).first()
        if is_subscribed(subscpt,subscbr):
            all_subscription = list(eval(subscpt.subscriptions))
            for x in all_subscription:
                if x == subscbr.user_id:
                    all_subscription.remove(x)
                    subscpt.no_of_subscrptn =len(all_subscription)
                    break
            subscpt.subscriptions = str(all_subscription)
            
            all_subscriber = list(eval(subscbr.subscribers))
            for x in all_subscriber:
                if x == subscpt.user_id:
                    all_subscriber.remove(x)
                    subscbr.no_of_subscrbs =len(all_subscriber)
                    break
            subscbr.subscribers = str(all_subscriber)
            db.session.commit()
    return redirect('/post/'+post_link)
def is_subscribed(user,channel):
    #subscription handle all the channel which has been subscribed by user
    #subscriber handle all the user which subscribe that channel
    all_subscription = list(eval(user.subscriptions))

    for subs in all_subscription:
        if subs == channel.user_id:
            return True
    return False
@app.route('/profile/<string:username>')
def profile(username):
    user = User.query.filter_by(name = username).first()
    if not user:
        return abort(404)
    elif user:
        posts = Post.query.filter_by(user = username).all()
        userdetail = UserDetail.query.filter_by(email = user.email).first()
        subscriber = Subscriber.query.filter_by(email = user.email).first()
        subscription = Subscription.query.filter_by(email = user.email).first()
        no_of_pst = len(Post.query.filter_by(email = user.email).all())
        if posts:
            posts.reverse()
            posts = posts[:5]
        return render_template('profile.html',user=user,posts = posts,usrdetail = userdetail,subscribr = subscriber.no_of_subscrbs,subscrptn = subscription.no_of_subscrptn,no_of_pst = no_of_pst)
