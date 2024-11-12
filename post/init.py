from flask import request,url_for,render_template,redirect,session,abort,flash,Blueprint
import datetime
import re
from utils.DBManager import db as postdb,Offers,Post,Subscriber,Subscription,User,UserDetail,UserVote
app = Blueprint("post",'postApp',static_folder='static',template_folder='templates')

def make_link(title):
    allword = re.sub(r'[^a-zA-Z0-9]', '-', title)
    link = allword+'-post'
    return link
def create_json(heading:list,content:list):
    data = {}
    data['allcont'] = []
#allcont structure like = [[heading1,content1],[heading2,content2].......[heading_n,content_n]]
    data['allcont'] = []
    for x in range(len(heading)):
        data['allcont'].append([heading[x],content[x]])
    return data
def reciepent(usr):
    all_rec = []
    allrecepient_no = list(eval(Subscriber.query.filter_by(user_id = usr.user_id).first().subscribers))
    all_usr = User.query.filter(User.user_id.in_(tuple(allrecepient_no))).all()
    for usr in all_usr:
        all_rec.append(str(usr.email))
    return all_rec

def is_subscribed(user,channel):
    #subscription handle all the channel which has been subscribed by user
    #subscriber handle all the user which subscribe that channel
    all_subscription = list(eval(user.subscriptions))

    for subs in all_subscription:
        if subs == channel.user_id:
            return True
    return False
@app.route('/addpost',methods = ['GET','POST'])
def addpost():
    usr = None
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
        if True:
            if(request.method == 'POST'):
                title = request.form.get('title')
                subtitle = request.form.get('subtitle')
                head:list = request.form.getlist('head')
                cont:list = request.form.getlist('cont')
                nowdt = datetime.datetime.now()
                dt = nowdt.ctime()
                post_link = make_link(title)
                if(title != ''):
                    content_file = create_json(heading=head,content = cont)
                    post = Post(title = title,subtitle = subtitle,content = str(content_file),email = usr.email,dt = dt,post_link = post_link,user = usr.name,suspend = False,total_vote = 0)
                    postdb.session.add(post)
                    postdb.session.commit()
                    flash('Added New Post')
                    return redirect('/')
        else:
            return "abort(404)"
            flash('Your pack has been expired')
            return redirect('/offer')
    elif 'user' not in session:
        return abort(404)
    return render_template('addpost.html',user = usr)

@app.route('/<string:post_link>', methods = ['GET'])
def post(post_link):
    liked = None
    channel = None
    subscribe = None
    usr = None
    pst = Post.query.filter_by(post_link = post_link,suspend = False).first()
    print(pst)
    username = pst.email
    if 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
        channel = Subscriber.query.filter_by(email = username).first()
        subscribe = is_subscribed(Subscription.query.filter_by(user_id = usr.user_id).first(),channel)
        liked = is_user_like_post(pst,usr)
    if not pst:
        return abort(404)
    data = dict(eval(pst.content))
    allcont = data['allcont']
    subscbr = Subscriber.query.filter_by(email = pst.email).first()
    return render_template('post.html',pst = pst,user = usr,content = allcont,total_subs = subscbr.no_of_subscrbs,liked = liked,subscribe = subscribe)

@app.route('/delete-post/<int:sno>')
def delete_post(sno):
    if not 'user' in session:
        return abort(404)
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        if user.admin:
            Post.query.filter_by(sno = sno).delete()
            postdb.session.commit()
            flash('Post Deleted Successfully')
    return redirect('/dashboard')
@app.route('/editpost',methods = ['GET'])
def editPost():
    user = None
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
    if request.method == 'GET' and user:
        post_no = request.args.get('post_no',-1)
        if post_no != -1:
            post = Post.query.filter_by(sno = post_no).first()
            if post:
                data = dict(eval(post.content))
                allcont = data['allcont']
                return render_template('addpost.html',content = allcont,pst = post,user = user)
        flash('Something Went Wronge')
        return redirect('/')
    return abort(404)
@app.route('/changepost/<string:post_link>',methods = ['POST'])
def changepost(post_link):
    if not 'user' in session:
        return abort(404)
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        if user.admin:
            if request.method == 'POST':
                post = Post.query.filter_by(post_link = post_link).first()
                title = request.form.get('title')
                subtitle = request.form.get('subtitle')
                head:list = request.form.getlist('head')
                cont:list = request.form.getlist('cont')
                nowdt = datetime.datetime.now()
                dt = nowdt.ctime()
                post_link = make_link(title)
                post.title = title
                post.subtitle = subtitle
                post.content = str(create_json(heading=head,content = cont))
                post.dt = dt
                post.post_link = post_link
                postdb.session.commit()
                flash('Post has been Edited')
                return redirect('/dashboard')
    return abort(404)
@app.route('/<string:post_link>/<string:choice>')
def Like_dislike(post_link,choice):
    if 'user' not in session:
        return redirect('/login')
    elif 'user' in session:
        usr = User.query.filter_by(email = session['user']).first()
        pst = Post.query.filter_by(post_link = post_link).first()
        if choice == 'like':
            likepost(pst,usr)
        elif choice == 'dislike' and pst.total_vote >0:
            dislikepost(pst,usr)
    return redirect('/post/'+pst.post_link)
def likepost(post,user):
    if not is_user_like_post(post,user):
        usrvote = UserVote.query.filter_by(user_id = user.user_id).first()
        if usrvote == None:
            all_up_post = []
            all_up_post.append(post.sno)
            post.total_vote = len(all_up_post)
            upvote = UserVote(user_id = user.user_id,email = user.email,upvote_post=str(all_up_post))
            postdb.session.add(upvote)
            postdb.session.commit()
        else:
            all_up_post = list(eval(usrvote.upvote_post))
            all_up_post.append(post.sno)
            post.total_vote += 1
            usrvote.upvote_post = str(all_up_post)
            postdb.session.commit()
def dislikepost(post,user):
    if is_user_like_post(post,user):
        usrvote = UserVote.query.filter_by(user_id = user.user_id).first()
        all_up_post = list(eval(usrvote.upvote_post))
        for x in all_up_post:
            if x == post.sno:
                all_up_post.remove(x)
                break
        post.total_vote -= 1
        usrvote.upvote_post = str(all_up_post)
        postdb.session.commit()
def is_user_like_post(post,user):
    if post != None and user != None:
        upvotedata = UserVote.query.filter_by(user_id = user.user_id).first()
        if upvotedata:
            upvotelist = list(eval(upvotedata.upvote_post))
            for p_sno in upvotelist:
                if int(p_sno) == post.sno:
                    return True
    return False
@app.route('/<string:action>/<int:p_id>')
def suspend(action,p_id):
    if 'user' in session:
        user = User.query.filter_by(email = session['user']).first()
        if user.admin:
            post = Post.query.filter_by(sno = int(p_id)).first()
            if action == 'suspend':
                post.suspend = True
                flash('Suspended')
            elif action == 'resume':
                post.suspend = False
                flash('Resume')
            postdb.session.commit()
            return redirect('/dashboard')
    return abort(404)
