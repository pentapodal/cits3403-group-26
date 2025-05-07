import json
import os
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf.file import FileStorage
from zipfile import ZipFile, BadZipFile
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import User


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
  potential_friends = [
    {"username": "Alice", "profile_picture": None},
    {"username": "Ryna", "profile_picture": None},
  ]

  return render_template('friends.html', title='Friends', friends=friends, potential_friends=potential_friends)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
  form = UploadForm()
  if form.validate_on_submit():
    file: FileStorage = form.file.data
    try:
      with ZipFile(file.stream) as archive:
        with archive.open('your_instagram_activity/likes/liked_posts.json') as f:
          likes_count = len(json.load(f)['likes_media_likes'])
      if not os.path.isdir(app.config['UPLOAD_PATH']):
        os.mkdir(app.config['UPLOAD_PATH'])
      path = os.path.join(app.config['UPLOAD_PATH'], f'{current_user.get_id()}.json')
      with open(path, 'w') as f:
        json.dump({'likes_count': likes_count}, f)
    except (BadZipFile, OSError) as error:
      flash(str(error))
    finally:
      return redirect(url_for('upload'))
  return render_template('upload.html', title='Upload', form=form)


@app.route('/overshare')
@app.route('/overshare/<username>')
@login_required
def overshare(username=None):
  if username is None:
    username = current_user.username
  return render_template('overshare.html', title='Overshare', username=username)
