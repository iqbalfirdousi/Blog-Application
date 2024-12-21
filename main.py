from flask import Flask, render_template,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
import json
from flask_mail import Mail


with open('config.json','r') as c:
    params= json.load(c) ["params"]

local_server= True
app = Flask(__name__)
app.secret_key='secret-super-key'
app.config.update(
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT= 465,
    MAIL_USE_SSL= True,
    MAIL_USERNAME= params['gmail-user'],
    MAIL_PASSWORD= params['gmail-password']
)
mail= Mail(app)

if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
 
db = SQLAlchemy(app)


class Contacts(db.Model):
    # sno, name, phone_no, email, msg, date
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    phone_no = db.Column(db.String(20), unique=True, nullable=False)
    msg= db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tag_line = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params, posts=posts)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
   
   
    if (request.method== 'POST'):
       username=request.form.get('uname')
       password=request.form.get('pass')
       if(username==params['admin_user'] and password==params['admin_password']):
           session['user']= username
           posts = Posts.query.all()
           return render_template('dashboard.html',params=params,posts=posts)
    else:      
         return render_template("login.html", params=params)
    
@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    # Print the current sno to help debug URL access issues
    print(f"Accessing /edit/{sno}")
    
    # Check if the user is logged in and authorized
    if "user" in session and session['user'] == params['admin_user']:
        if request.method == "POST":
            # Fetch form data
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            # Check if creating a new post
            if sno == '0':
                print("Creating a new post.")
                new_post = Posts(title=box_title, slug=slug, content=content, tag_line=tline, img_file=img_file, date=date)
                db.session.add(new_post)
                db.session.commit()
                return redirect('/dashboard')  # Redirect after creating a new post
            else:
                # Update an existing post
                post = Posts.query.filter_by(sno=sno).first()
                if post:
                    print("Editing an existing post.")
                    post.title = box_title
                    post.tag_line = tline
                    post.slug = slug
                    post.content = content
                    post.img_file = img_file
                    post.date = date
                    db.session.commit()
                    return redirect('/edit/' + sno)  # Redirect after updating
                else:
                    print("Post not found, redirecting to dashboard.")
                    return redirect('/dashboard')

        # Handle GET request to fetch the post
        post = Posts.query.filter_by(sno=sno).first() if sno != '0' else None
        print(f"Rendering edit page for {'new post' if sno == '0' else 'existing post'}")
        return render_template('edit.html', params=params, post=post)
    else:
        print("User not authorized, redirecting to dashboard.")
        return redirect('/dashboard')

@app.route("/contact", methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        # Add entry to the database
       
        name= request.form.get('name')
        email= request.form.get('email')
        phone= request.form.get('phone')
        message= request.form.get('message')

        entry= Contacts(name= name, email= email, phone_no= phone, msg= message) 
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from blog' + name,
                          sender=email,
                          recipients= [params['gmail-user']],
                          body= message + "\n" + phone
                          )
    return render_template('contact.html',params=params)

app.run(debug=True)

