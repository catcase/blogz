from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'dnfh82hfuiwhkfazz'

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    post = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post, owner):
        self.title = title
        self.post = post
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(30))
    blogs = db.relationship('Entry', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/blog', methods=['GET'])
def blog():

    id = request.args.get('id')
    user_id = request.args.get('user')

    blogs = Entry.query.all()

    if id:
        blog = Entry.query.get(id)
        return render_template('submit.html', item=blog)
    if user_id:
        user = User.query.get(user_id)
        blogs = user.blogs
        
    return render_template('blog.html', submitted=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def add():
    blog_title = ""
    blog_title_error = ""

    blog_entry = ""
    blog_entry_error = ""

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['blog_title']
        post = request.form['blog_entry']

        if not title:
            blog_title_error = "Title cannot be blank"
        else:
            blog_title_error = ""

        if not post:
            blog_entry_error = "Body cannot be blank"
        else:
            blog_entry_error = ""
    
        if not blog_title_error and not blog_entry_error:
            new_entry = Entry(title, post, owner)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id=' + str(new_entry.id)) #redirect uses GET method
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_title_error=blog_title_error, blog_entry=blog_entry, blog_entry_error=blog_entry_error)            
    else:
        return render_template('newpost.html')


@app.route('/singleentry')
def submit():
    return render_template('submit.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'logged_in')
            return redirect('/newpost')
        elif not username and not password:
            flash('Username and password cannot be blank')
        else:
            flash('Username or password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    username = ""
    username_error = ""

    password = ""
    password_error = ""

    verify = ""
    verify_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error = False

        if not username:
            flash('Username cannot be blank', 'error')
            error = True
        elif " " in username:
            flash('Username cannot contain spaces', 'error')
            error = True
        elif len(username) < 3 or len(username) > 20:
            flash('Username must be between 3 & 20 characters', 'error')
            error = True

        if not password:
            flash('Password cannot be blank', 'error')
            error = True
        elif len(password) < 3:
            flash('Password must be greater than 3 characters', 'error')
            error = True

        if not verify:
            flash('Please verify password', 'error')
            error = True
        elif verify != password:
            flash('Passwords do not match', 'error')
            error = True

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user and not error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        elif existing_user:
            flash('Username already exists', 'error')
            error = True

    return render_template('signup.html')

# need to return redirect to blog; redirects to login
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)




if __name__ == '__main__':
    app.run()