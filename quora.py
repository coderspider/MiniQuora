from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from sqlalchemy import func
from datetime import datetime
import socket

d = datetime.today()

from sqlalchemy import Table
import json

app = Flask(__name__)
mail=Mail(app)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] ='super-secret-key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog_one.db'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'joelvinaykumar@gmail.com'
app.config['MAIL_PASSWORD'] = 'madhudarling'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

db=SQLAlchemy(app)

class Login(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(24))

    def __init__(self, email,username, password,):
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Entry %r %r %r>' % (self.email,self.username, self.password)


class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    author = db.Column(db.String(20))
    tag = db.Column(db.String(20))
    date_posted = db.Column(db.String(50))
    content = db.Column(db.Text)
    authenticated = db.Column(db.Boolean())

    def __init__(self, title, author, tag, date_posted, content, authenticated):
        self.title = title
        self.author = author
        self.tag = tag
        self.date_posted = date_posted
        self.content = content
        self.authenticated = authenticated

    def __repr__(self):
        return '<Entry %r %r %r %r %r %r>' % (self.title, self.author, self.tag, self.date_posted, self.content, self.authenticated)

class Comments(db.Model):
    serial_no = db.Column(db.Integer ,primary_key=True)
    comment_id = db.Column(db.Integer(),db.ForeignKey('blogpost.id'))
    comment = db.Column(db.String(200))
    date = db.Column(db.String(50))
    author = db.Column(db.String(50))
    authenticated = db.Column(db.Boolean())

    def __init__(self, serial_no, comment_id, comment, date, author, authenticated):
        self.serial_no = serial_no
        self.comment_id = comment_id
        self.comment = comment
        self.date = date
        self.author = author
        self.authenticated = authenticated
    def __repr__(self):
        return '<Entry %r %r %r %r %r %r>' % (self.serial_no, self.comment_id, self.comment, self.date, self.author, self.authenticated)
# Create the table
db.create_all()


def authenticate(e, p):
    details= Login.query.filter_by(email=e).filter_by(password=p).all()
    if(len(details)>0):
        return True
    else:
        return False

@app.route('/',methods=['GET','POST'])
def index():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    if request.method == 'POST':
        if session['logged_in']==True:
            title = request.form['question']
            author = session['log_user']
            content = request.form['content']
            tag = request.form['tag']
            date_p=d.strftime("%d-%B-%Y %H:%M:%S")
            auth = False
            post = Blogpost(title=title, author=author, content=content, date_posted=date_p, tag=tag, authenticated =auth)

            db.session.add(post)
            db.session.commit()
            msg = Message('New post by '+request.form['name'], sender = 'joelvinaykumar@gmail.com', recipients = ['joelvinaykumar@riseup.net'])
            msg.body = "Hello Joel,\n"+author+" posted this.\n"+'"'+request.form['content']+'"'+"on"+date_p
            mail.send(msg)
            
            return render_template('index.html',posts=posts)
        else:
            return redirect(url_for('login'))
    else:
        if session['logged_in'] == True:
            posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
            return render_template('index.html',posts=posts)
        else:
            return redirect(url_for('login'))

@app.route('/post/<int:post_id>',methods=['GET','POST'])
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    all_coms = Comments.query.order_by(Comments.comment).all()
    if request.method=='POST':
        serial_no = 1
        comment_id = post_id
        comment = request.form.get('com')
        date_p = d.strftime("%d-%B-%Y %H:%M:%S")
        author = session['log_user']
        authenticated =False
        commy = Comments(serial_no=serial_no, comment_id=comment_id, comment=comment, date=date_p, author=author, authenticated=authenticated)

        db.session.add(commy)
        db.session.commit()

        all_coms = Comments.query.order_by(Comments.comment).all()
        return render_template('post.html', post=post, comments=all_coms)
    else:
        return render_template('post.html', post=post, comments=all_coms)

@app.route('/admin',methods=['GET','POST'])
def admin():
    list_unapproved = Blogpost.query.filter_by(authenticated=False).all()
    if request.method == 'POST':
        var = request.form['approve']
        print(var)
        return render_template('admin.html',pots = list_unapproved)
    else:
        return render_template('admin.html',pots = list_unapproved)

@app.route('/logout')
def logout():
    # post = Blogpost.query.filter_by(id=post_id).one()
    if session['logged_in'] == True:
        session['logged_in'] = False
        posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
        return render_template('index.html',posts=posts)
    else:
        return render_template('index.html')

@app.route('/sign_up',methods=['GET','POST'])
def sign_up():
    error = None
    if request.method== 'GET':
        return render_template('sign_up.html')
    else:
        uname = request.form.get('user')
        email = request.form.get('uname')
        pwd = request.form.get('pwd')
        new_user = Login(email,uname,pwd)
        db.session.add(new_user)
        db.session.commit()
        # msg = Message('New account created', sender = 'joelvinaykumar@gmail.com', recipients = uname)
        # msg.body = "Hello,\nThere is a new account created.\n"+'"Email:'+uname+'"'
        # mail.send(msg)
        error= "New account created for "+request.form.get('user')
        return render_template('sign_up.html',error=error)

# @app.route('/create_post',methods=['GET','POST'])
# def create_post():
#     if request.method == 'POST':
#         if session['logged_in']==True:
#             title = request.form['question']
#             author = session['log_user']
#             content = request.form['content']
#             tag = request.form['tag']
#             date_p=d.strftime("%d-%B-%Y %H:%M:%S")
#             post = Blogpost(title=title, author=author, content=content, date_posted=date_p, tag=tag)

#             db.session.add(post)
#             db.session.commit()
#             msg = Message('New post by '+request.form['name'], sender = 'joelvinaykumar@gmail.com', recipients = ['joelvinaykumar@riseup.net'])
#             msg.body = "Hello,\n"+author+" posted this.\n"+'"'+request.form['content']+'"'+"on"+date_p
#             mail.send(msg)
#             posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
#             return redirect(url_for('index',posts=posts))
#         else:
#             return redirect(url_for('login'))
#     else:
#         if session['logged_in'] == True:
#             posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
#             return render_template('index.html',posts=posts)
#         else:
#             return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if(authenticate(request.form['email'], request.form['password'])):
            session['logged_in'] = True
            a= request.form['email']
            session['log_user'] = Login.query.filter_by(email=a).one().username
            posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
            return render_template('index.html',posts=posts)
        else:
            error='Invalid credentials'
    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
