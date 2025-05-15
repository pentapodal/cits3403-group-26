import json
import os
from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf.file import FileStorage
from zipfile import ZipFile, BadZipFile
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, UploadForm, EmptyForm
from app.models import User
from app.utils import process_zip_and_save
current_user: User


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


@app.route('/following')
@login_required
def following():
  form = EmptyForm()
  following_list = [
    {'username': 'Chen ', 'profile_picture': 'chen.jpg'},
    {'username': 'Andrea', 'profile_picture': 'andrea.png'},
    {'username': 'Jia', 'profile_picture': 'jia.png'},
    {'username': 'David', 'profile_picture': None},
    {'username': 'Eve', 'profile_picture': None},
  ]
  # following_list = db.session.scalars(current_user.following.select()).all()
  return render_template('following.html', title='Following', form=form, following=following_list)


@app.route('/followers')
@login_required
def followers():
  form = EmptyForm()
  followers_list = [
    {'username': 'Chen ', 'profile_picture': 'chen.jpg'},
    {'username': 'Andrea', 'profile_picture': 'andrea.png'},
    {'username': 'Jia', 'profile_picture': 'jia.png'},
    {'username': 'Anna', 'profile_picture': None},
    {'username': 'Ryan', 'profile_picture': None},
  ]
  return render_template('followers.html', title='Followers', form=form, followers=followers_list)


@app.route('/follow-requesters')
@login_required
def follow_requesters():
  requesters_list = [
    {'username': 'Chen ', 'profile_picture': 'chen.jpg'},
    {'username': 'Andrea', 'profile_picture': 'andrea.png'},
    {'username': 'Jia', 'profile_picture': 'jia.png'},
    {'username': 'Anna', 'profile_picture': None},
    {'username': 'Ryan', 'profile_picture': None},
  ]
  return render_template('follow-requesters.html', title='Follow Requests', friend_requests=requesters_list)

@app.route('/follow-requesting')
@login_required
def follow_requesting():
  requesting_list = [
    {'username': 'Chen ', 'profile_picture': 'chen.jpg'},
    {'username': 'Andrea', 'profile_picture': 'andrea.png'},
    {'username': 'Jia', 'profile_picture': 'jia.png'},
    {'username': 'Anna', 'profile_picture': None},
    {'username': 'Ryan', 'profile_picture': None},
  ]
  return render_template('follow-requesting.html', title='Follow Requesting', friend_requests=requesting_list)


@app.route('/send_follow_request/<username>', methods=['POST'])
@login_required
def send_follow_request(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
      flash(f'User {username} not found.')
    elif user == current_user:
      flash('You cannot send a follow request to yourself!')
    elif current_user.is_follow_requesting(user):
      flash(f'You have already sent a follow request to {username}!')
    elif current_user.is_following(user):
      flash(f'You are already following {username}!')
    else:
      current_user.send_follow_request(user)
      db.session.commit()
      flash(f'You have sent a follow request to {username}.')
  return redirect(url_for('follow_requesting'))


@app.route('/cancel_follow_request/<username>', methods=['POST'])
@login_required
def cancel_follow_request(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
      flash(f'User {username} not found.')
    elif user == current_user:
      flash('You cannot cancel a follow request to yourself!')
    elif not current_user.is_follow_requesting(user):
      flash(f'You have not sent a follow request to {username}!')
    else:
      current_user.cancel_follow_request(user)
      db.session.commit()
      flash(f'You have cancelled a follow request to {username}.')
  return redirect(url_for('follow_requesting'))


@app.route('/accept_follow_requester/<username>', methods=['POST'])
@login_required
def accept_follow_requester(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
      flash(f'User {username} not found.')
    elif user == current_user:
      flash('You cannot accept a follow request from yourself!')
    elif not current_user.is_follow_requested_by(user):
      flash(f'You have not received a follow request from {username}!')
    elif current_user.is_followed_by(user):
      flash(f'You are already being followed by {username}!')
    else:
      current_user.accept_follow_requester(user)
      db.session.commit()
      flash(f'You have accepted a follow request from {username}.')
  return redirect(url_for('follow_requesters'))


@app.route('/dismiss_follow_requester/<username>', methods=['POST'])
@login_required
def dismiss_follow_requester(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
      flash(f'User {username} not found.')
    elif user == current_user:
      flash('You cannot dismiss a follow request from yourself!')
    elif not current_user.is_follow_requested_by(user):
      flash(f'You have not received a follow request from {username}!')
    else:
      current_user.dismiss_follow_requester(user)
      db.session.commit()
      flash(f'You have dismissed a follow request from {username}.')
  return redirect(url_for('follow_requesters'))


@app.route('/stop_following/<username>', methods=['POST'])
@login_required
def stop_following(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
      flash(f'User {username} not found.')
    elif user == current_user:
      flash('You cannot stop following yourself!')
    elif not current_user.is_following(user):
      flash(f'You are not following {username}!')
    else:
      current_user.stop_following(user)
      db.session.commit()
      flash(f'You have stopped following {username}.')
  return redirect(url_for('following'))


@app.route('/remove_follower/<username>', methods=['POST'])
@login_required
def remove_follower(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is None:
      flash(f'User {username} not found.')
    elif user == current_user:
      flash('You cannot stop following yourself!')
    elif not current_user.is_followed_by(user):
      flash(f'You are not being followed by {username}!')
    else:
      current_user.remove_follower(user)
      db.session.commit()
      flash(f'You have removed the follower {username}.')
  return redirect(url_for('followers'))


@app.route('/search_users/<query>')
@login_required
def search_users(query):
  # Need to use .from_statement() because selecting ORM, see:
  # https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-entities-from-unions-and-other-set-operations
  result: sa.ScalarResult[User] = db.session.scalars(
    sa.select(User).from_statement(
      sa.select(User)
      .where(User.username.ilike(f'%{query}%'))
      .except_(
        current_user.follow_requesting.select(),
        current_user.following.select()
      )
    )
  )
  return {"result": [
    {"username": user.username, "is_follower": current_user.is_followed_by(user)}
    for user in result
  ]}


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file: FileStorage = form.file.data
        try:
            path = process_zip_and_save(file.stream, app.config['UPLOAD_PATH'], current_user.username)
            flash(f'File Successfully Uploaded')
            return redirect(url_for('overshare', username=current_user.username))
        except (BadZipFile, OSError) as error:
            flash(str(error))
    return render_template('upload.html', title='Upload', form=form)


@app.route('/overshare')
@app.route('/overshare/<username>')
@login_required
def overshare(username=None):
    if username is None:
        username = current_user.username

    json_file_path = os.path.join(app.config['UPLOAD_PATH'], f'{username}.json')

    if not os.path.isfile(json_file_path): 
        flash("No data available for this user.")
        return redirect(url_for('upload'))

    with open(json_file_path, 'r') as json_file:
        user_data = json.load(json_file)

    return render_template('overshare.html', title='Overshare', username=username, user_data=user_data)
