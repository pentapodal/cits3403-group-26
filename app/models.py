from datetime import datetime, timezone
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


follow_requests = sa.Table(
  'follow_requests',
  db.metadata,
  sa.Column('requester_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
  sa.Column('requested_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)


follows = sa.Table(
  'follows',
  db.metadata,
  sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
  sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)


class User(UserMixin, db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
  email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
  password_hash: so.Mapped[str | None] = so.mapped_column(sa.String(256))

  posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

  follow_requesting: so.WriteOnlyMapped['User'] = so.relationship(
    secondary=follow_requests,
    primaryjoin=(id == follow_requests.c.requester_id),
    secondaryjoin=(follow_requests.c.requested_id == id),
    back_populates='follow_requesters'
  )
  follow_requesters: so.WriteOnlyMapped['User'] = so.relationship(
    secondary=follow_requests,
    primaryjoin=(id == follow_requests.c.requested_id),
    secondaryjoin=(follow_requests.c.requester_id == id),
    back_populates='follow_requesting'
  )

  following: so.WriteOnlyMapped['User'] = so.relationship(
    secondary=follows,
    primaryjoin=(id == follows.c.follower_id),
    secondaryjoin=(follows.c.followed_id == id),
    back_populates='followers'
  )
  followers: so.WriteOnlyMapped['User'] = so.relationship(
    secondary=follows,
    primaryjoin=(id == follows.c.followed_id),
    secondaryjoin=(follows.c.follower_id == id),
    back_populates='following'
  )

  def __repr__(self):
    return '<User {}>'.format(self.username)

  def set_password(self, password: str):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password: str):
    return check_password_hash(self.password_hash, password)

  def is_follow_requesting(self, user: 'User'):
    query = self.follow_requesting.select().where(User.id == user.id)
    return db.session.scalar(query) is not None

  def is_follow_requested_by(self, user: 'User'):
    query = self.follow_requesters.select().where(User.id == user.id)
    return db.session.scalar(query) is not None

  def is_following(self, user: 'User'):
    query = self.following.select().where(User.id == user.id)
    return db.session.scalar(query) is not None

  def is_followed_by(self, user: 'User'):
    query = self.followers.select().where(User.id == user.id)
    return db.session.scalar(query) is not None

  def send_follow_request(self, user: 'User'):
    if not (self.is_follow_requesting(user) or self.is_following(user)):
      self.follow_requesting.add(user)

  def cancel_follow_request(self, user: 'User'):
    if self.is_follow_requesting(user):
      self.follow_requesting.remove(user)

  def dismiss_follow_requester(self, user: 'User'):
    if self.is_follow_requested_by(user):
      self.follow_requesters.remove(user)

  def accept_follow_requester(self, user: 'User'):
    self.dismiss_follow_requester(user)
    if not self.is_followed_by(user):
      self.followers.add(user)

  def stop_following(self, user: 'User'):
    if self.is_following(user):
      self.following.remove(user)

  def remove_follower(self, user: 'User'):
    if self.is_followed_by(user):
      self.followers.remove(user)

  def follow_requesting_count(self):
    query = sa.select(sa.func.count()).select_from(self.follow_requesting.select().subquery())
    return db.session.scalar(query)

  def follow_requesters_count(self):
    query = sa.select(sa.func.count()).select_from(self.follow_requesters.select().subquery())
    return db.session.scalar(query)

  def followers_count(self):
    query = sa.select(sa.func.count()).select_from(self.followers.select().subquery())
    return db.session.scalar(query)

  def following_count(self):
    query = sa.select(sa.func.count()).select_from(self.following.select().subquery())
    return db.session.scalar(query)

  def search_unfollowed(self, q: str):
    # Need to use .from_statement() because selecting ORM, see:
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-entities-from-unions-and-other-set-operations
    query = sa.select(User).from_statement(
      sa.select(User)
      .where(User.username.ilike(f'%{q}%'))
      .where(User.username != self.username)
      .except_(
        self.follow_requesting.select(),
        self.following.select()
      )
    )
    return db.session.scalars(query)

  def following_posts(self):
    # Eventually want to rework this into following Overshares
    Author = so.aliased(User)
    Follower = so.aliased(User)
    return (
      sa.select(Post)
      .join(Post.author.of_type(Author))
      .join(Author.followers.of_type(Follower))
      .where(Follower.id == self.id)
      .order_by(Post.timestamp.desc())
    )


@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))


class Post(db.Model):
  id: so.Mapped[int] = so.mapped_column(primary_key=True)
  body: so.Mapped[str] = so.mapped_column(sa.String(140))
  timestamp: so.Mapped[datetime] = so.mapped_column(
    index=True, default=lambda: datetime.now(timezone.utc))
  user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

  author: so.Mapped[User] = so.relationship(back_populates='posts')

  def __repr__(self):
    return '<Post {}>'.format(self.body)
