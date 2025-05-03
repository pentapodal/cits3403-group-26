from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
import zipfile

ALLOWED_EXTENSIONS = {'zip'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
  posts = [
    {
      'author': {'username': 'John'},
      'body': 'Beautiful day in Portland!'
    },
    {
      'author': {'username': 'Susan'},
      'body': 'The Avengers movie was so cool!'
    }
  ]
  return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = LoginForm()
  if form.validate_on_submit():
    user = db.session.scalar(
      sa.select(User).where(User.username == form.username.data))
    if user is None or not user.check_password(form.password.data):
      flash('Invalid username or password')
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
      next_page = url_for('home')
    return redirect(next_page)
  return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash('Congratulations, you are now a registered user!')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)


@app.route('/home')
@login_required
def home():
  return render_template('home.html', title='Home')


@app.route('/friends')
#@login_required # Uncomment this line to require login for the friends page
def friends():
  friends = [
    {'username': 'Chen ', 'profile_picture': 'chen.jpg'},
    {'username': 'Andrea', 'profile_picture': 'andrea.png'},
    {'username': 'Jia', 'profile_picture': 'jia.png'},
    {'username': 'David', 'profile_picture': None},
    {'username': 'Eve', 'profile_picture': None},
  ]
  return render_template('friends.html', title='Friends', friends=friends)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If no file is selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # Check if the file is allowed
        if file and allowed_file(file.filename):
            try:
                # Verify if the file is a valid ZIP file
                # Future ref: We will have to analyze ZIP file by calling a function in this try block
                # from utlis.py
                with zipfile.ZipFile(file.stream, 'r') as zip_ref:
                    flash(f'Successfully received ZIP file: {file.filename}')
            except zipfile.BadZipFile:
                flash('The uploaded file is not a valid ZIP file.')
            return redirect(url_for('upload'))
        else:
            flash('Only ZIP files are allowed')
            return redirect(request.url)
    return render_template('upload.html', title='Upload')


@app.route('/overshare')
@app.route('/overshare/<username>')
@login_required
def overshare(username=None):
  if username is None:
    username = current_user.username
  return render_template('overshare.html', title='Overshare', username=username)
