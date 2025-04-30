from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, SearchForm
from app.models import User, Friend


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
@login_required
def friends():
    # Fetch the current user's friends
    friends = db.session.scalars(sa.select(User).join(Friend, Friend.friend_id == User.id).where(Friend.user_id == current_user.id, Friend.status == 'accepted')).all()
    return render_template('friends.html', title='Friends', friends=friends)


@app.route('/upload')
@login_required
def upload():
  return render_template('upload.html', title='Upload')


@app.route('/overshare')
@app.route('/overshare/<username>')
@login_required
def overshare(username=None):
  if username is None:
    username = current_user.username
  return render_template('overshare.html', title='Overshare', username=username)


@app.route('/add_friend/<int:friend_id>', methods=['POST'])
@login_required
def add_friend(friend_id):
    # Check if the friendship already exists
    existing_friendship = db.session.scalar(sa.select(Friend).where((Friend.user_id == current_user.id) & (Friend.friend_id == friend_id)))
    if existing_friendship:
        flash('You are already friends with this user.')
        return redirect(url_for('friends'))

    # Add the friendship
    new_friendship = Friend(user_id=current_user.id, friend_id=friend_id)
    db.session.add(new_friendship)
    db.session.commit()
    flash('Friend added successfully!')
    return redirect(url_for('friends'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    users = []
    if form.validate_on_submit():
        users = db.session.scalars(sa.select(User).where(User.username.ilike(f"%{form.username.data}%"))).all()
    return render_template('search.html', title='Search Users', form=form, users=users)


@app.route('/send_friend_request/<int:friend_id>', methods=['POST'])
@login_required
def send_friend_request(friend_id):
    # Check if a request already exists
    existing_request = db.session.scalar(
        sa.select(Friend).where((Friend.user_id == current_user.id) & (Friend.friend_id == friend_id)))
    if existing_request:
        flash('Friend request already sent.')
        return redirect(url_for('search'))

    # Create a new friend request
    friend_request = Friend(user_id=current_user.id, friend_id=friend_id, status='pending')
    db.session.add(friend_request)
    db.session.commit()
    flash('Friend request sent!')
    return redirect(url_for('search'))


@app.route('/friend_requests')
@login_required
def friend_requests():
    # Fetch incoming friend requests
    requests = db.session.scalars(sa.select(Friend).where((Friend.friend_id == current_user.id) & (Friend.status == 'pending'))).all()
    return render_template('friend_requests.html', title='Friend Requests', requests=requests)


@app.route('/accept_friend_request/<int:request_id>', methods=['POST'])
@login_required
def accept_friend_request(request_id):
    # Accept the friend request
    friend_request = db.session.get(Friend, request_id)
    if friend_request and friend_request.friend_id == current_user.id:
        friend_request.status = 'accepted'
        # Create a reciprocal friendship
        reciprocal_friendship = Friend(user_id=current_user.id, friend_id=friend_request.user_id, status='accepted')
        db.session.add(reciprocal_friendship)
        db.session.commit()
        flash('Friend request accepted!')
    else:
        flash('Invalid friend request.')
    return redirect(url_for('friend_requests'))
