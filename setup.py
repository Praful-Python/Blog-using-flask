from flask import Flask, render_template, request, session, redirect, flash,url_for
from datetime import datetime
from werkzeug.utils import secure_filename
import json, os, math
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'super_secret_key'

with open('PyPraa.json', 'r') as c:
    scripts = json.load(c)["scripts"]

with open('PyPraa.json', 'r') as d:
    database = json.load(d)["database"]

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=scripts['gmail-user'],
    MAIL_PASSWORD=scripts['password']
)
mail = Mail(app)

if():
    app.config['SQLALCHEMY_DATABASE_URI'] = database['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = database['prod_url']


app.config['UPLOAD_FOLDER'] = scripts['uploader_location']

db = SQLAlchemy(app)

class Contact(db.Model):
    '''
    no, name email, mobile_numb er, message, d&t
    '''
    no = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    mobile_number = db.Column\
        (db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    dnt = db.Column(db.String(12), nullable=True)

class Blog(db.Model):
    no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False)
    tafline = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

@app.route("/contact", methods = ['GET','POST'])
def index():
    if (request.method == 'POST'):
        '''Add ry to the database'''
        '''
        no, name email, mobile_number, message, d&t
        '''
        fname = request.form.get('fname')
        email = request.form.get('email')
        phone = request.form.get('number')
        mssag = request.form.get('message')
        entry = Contact(name=fname, mobile_number=phone, message=mssag, dnt=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New msg from blog user ' + fname,
                          sender=email,
                          recipients=[scripts['gmail-user'], 'fmrathod1818@gmail.com'],
                          body = fname +"  "+ mssag + "\n" + phone
        )
        return render_template('index.html', scripts=scripts, database=database)
    return render_template('index.html', scripts=scripts, database=database)

@app.route("/edit/add_blog", methods = ['GET','POST'])
def add_blog():
        if(request.method == 'POST'):
            edit_title = request.form.get('title')
            edit_content = request.form.get('content')
            edit_img_file = request.files['img_file']
            edit_tagline = request.form.get('tagline')
            edit_slug = request.form.get('slug')
            edit_date = datetime.now()
            edit_img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(edit_img_file.filename)))
            blog = Blog(title=edit_title, content=edit_content, tafline=edit_tagline, slug=edit_slug, img_file=edit_img_file.filename, date=edit_date)
            db.session.add(blog)
            db.session.commit()
            blog = Blog.query.filter_by().all()[0:scripts['no_of_post']]
            return redirect('/blogs')
        #blog = Blog.query.filter_by().all()[0:scripts['no_of_post']]
        return render_template('add_blog.html', scripts=scripts, database=database)


@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if session.get('logged_in'):
        if(request.method == 'POST'):
            edit_title = request.form.get('title')
            edit_content = request.form.get('content')
            edit_img_file = request.files['img_file']
            edit_img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(edit_img_file.filename)))
            edit_tagline = request.form.get('tagline')
            edit_slug = request.form.get('slug')
            edit_date = datetime.now()
            blog = Blog.query.filter_by(no=sno).first()
            blog.title = edit_title
            blog.content = edit_content
            blog.tafline = edit_tagline
            blog.img_file = edit_img_file.filename
            blog.data = edit_date
            blog.slug = edit_slug
            db.session.commit()
            return redirect('/dashboard')
    blog = Blog.query.filter_by(no=sno).first()
    return render_template('edit.html', scripts=scripts, database=database, blog=blog)


@app.route("/dashboard", methods= ['POST', 'GET'])
def do_admin_login():
    if session.get('logged_in'):
        blog = Blog.query.filter_by().all()
        return render_template('dashboard.html', scripts=scripts, database=database, blog=blog)

    if request.form.get('name') == scripts['username'] and request.form.get('password') == scripts['password']:
        session['logged_in'] = True
        flash("You are successfully logged in")
        blog = Blog.query.filter_by().all()
        return render_template('dashboard.html', scripts=scripts, database=database, blog=blog)
    else:
        flash('wrong password!')
        return login()

@app.route("/")
def home():
    return render_template('index.html', scripts=scripts, database=database)

@app.route("/blogs/<string:blog_slug>", methods = ['GET', 'POST'])
def blogconfig(blog_slug):
    blog = Blog.query.filter_by(slug=blog_slug).first()
    return render_template('blog_slug.html', scripts=scripts, blog=blog, database=database)


@app.route("/blogs", methods=['POST', 'GET'])
def blog():
    blog = Blog.query.filter_by().all()
    print(dir(blog))
    last = math.ceil(len(blog)/int(scripts['no_of_post']))
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    blog = blog[(page-1)*int(scripts['no_of_post']):(page-1)*int(scripts['no_of_post']) + int(scripts['no_of_post'])]
    if(page==1):
        prev="#"
        next = "blogs?page="+str(page+1)
    elif(page==last):
        prev = "blogs?page="+str(page-1)
        next = "#"
    else:
        prev = "blogs?page="+str(page-1)
        next = "blogs?page="+str(page+1)
    return render_template('blog.html', scripts=scripts, database=database, blog=blog, prev=prev, next=next)



@app.route("/Login")
def login():
    if not session.get('logged_in'):
        return render_template('login.html', scripts=scripts)
    else:
        blog = Blog.query.filter_by().all()
        return render_template('dashboard.html', scripts=scripts, database=database, blog=blog)

@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    flash("logged out Completely")
    return redirect('/')

@app.route("/delete/<string:sno>", methods= ['POST', 'GET'])
def delete(sno):
    if session.get('logged_in'):
        blog = Blog.query.filter_by(no=sno).first()
        db.session.delete(blog)
        db.session.commit()
    return redirect('/dashboard')

if __name__ == '__main__' :
    app.run(debug=True)