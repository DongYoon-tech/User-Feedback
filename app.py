from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'SECRET123'

connect_db(app)
db.create_all()
debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """Home Page redirect to register page"""

    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    """Register User page"""
    
    form = RegisterForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        email = form.email.data
        first = form.first_name.data
        last = form.last_name.data

        user = User.register(name, pwd, email, first, last)
        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
        flash("Successfully registered!", 'success')
        return redirect(f"/users/{user.username}")

    else:
        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data
        user = User.authenticate(name, pwd)

        if user:
            session['username'] = user.username
            flash("Successfully log in!", 'success')
            return redirect(f"/users/{user.username}")

        else:
            form.username.errors = ["Invalid User"]

    return render_template("login.html", form=form)

@app.route("/users/<username>")
def show_user(username):
    """Show user info"""

    if session['username'] != username:
        flash("You must be logged in to view!",'danger')
        return redirect("/")

    else:
        users = User.query.get_or_404(username)
        return render_template("show.html", users=users)


@app.route("/users/<username>/delete", methods=['POST'])
def delete_user(username):
    """Delete user form"""

    if 'username' not in session:
        flash("Please login first!", 'danger')
        return redirect('/login')

    user = User.query.get_or_404(username)
    
    if username == session['username']:
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        flash(f"{user.username} deleted!", 'info')
        return redirect('/')

@app.route('/users/<username>/feedback/add', methods=['GET','POST'])
def user_feedback(username):
    """Add User feedback form"""

    if session['username'] != username:
        flash("You need to log in first!", 'danger')
        return redirect("/")

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title,content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        flash("Feedback created!", 'success')
        return redirect(f"/users/{feedback.user.username}")

    else:
        return render_template("feedback.html", form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET','POST'])
def update_feedback(feedback_id):
    """Edit User's feedback"""

    if "username" not in session:
        flash("Please login first!", 'danger')
        return redirect("/")

    form =  FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback.query.get_or_404(feedback_id)
        feedback.title = title
        feedback.content = content
        db.session.commit()
        flash("Feedback updated!", 'info')
        return redirect(f"/users/{feedback.user.username}")

    else:
        return render_template("feedback.html", form=form)

@app.route("/feedback/<int:feedback_id>/delete", methods=['POST'])
def delete_feedback(feedback_id):
    """Delete user's feedback"""

    if 'username' not in session:
        flash("Please login first!", 'danger')
        return redirect('/login')

    feedback = Feedback.query.get_or_404(feedback_id)

    if feedback.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", 'info')
        return redirect(f'/users/{feedback.username}')

    flash("You don't have permission to do that!")
    return redirect('/')

@app.route("/logout")
def logout():

    session.pop("username")
    flash('Succesfully Logout!', 'success')
    return redirect("/")
