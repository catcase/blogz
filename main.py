from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:helloworld@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    post = db.Column(db.String(500))

    def __init__(self, title, post):
        self.title = title
        self.post = post

@app.route('/blog')
def index():
    submitted = Entry.query.all()
    return render_template('blog.html', submitted=submitted)


@app.route('/newpost', methods=['GET', 'POST'])
def add():
    blog_title = ""
    blog_title_error = ""

    blog_entry = ""
    blog_entry_error = ""

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
            new_entry = Entry(title, post)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog') #redirect uses GET method
        else:
            return render_template('newpost.html', blog_title=blog_title, blog_title_error=blog_title_error, blog_entry=blog_entry, blog_entry_error=blog_entry_error)            
    else:
        return render_template('newpost.html')

# @app.route('/submit', methods=['GET','POST'])
# def submit():
#     return render_template('submit.html')


if __name__ == '__main__':
    app.run()