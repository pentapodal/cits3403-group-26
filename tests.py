import os
from typing import override

from config import TestingConfig
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import create_application, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
  @override
  def setUp(self):
    self.app = create_application(TestingConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  @override
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_password_hashing(self):
    u = User(username='susan', email='susan@example.com')
    u.set_password('cat')
    self.assertFalse(u.check_password('dog'))
    self.assertTrue(u.check_password('cat'))


class UserModelFollowCase(unittest.TestCase):
  @override
  def setUp(self):
    self.app = create_application(TestingConfig)
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

    u1 = User(username='john', email='john@example.com')
    u2 = User(username='susan', email='susan@example.com')
    db.session.add(u1)
    db.session.add(u2)
    u1.send_follow_request(u2)
    db.session.commit()
    self.assertTrue(u1.is_follow_requesting(u2))
    self.assertTrue(u2.is_follow_requested_by(u1))
    self.assertEqual(u1.follow_requesting_count(), 1)
    self.assertEqual(u2.follow_requesters_count(), 1)
    u1_follow_requesting = db.session.scalars(u1.follow_requesting.select()).all()
    u2_follow_requesters = db.session.scalars(u2.follow_requesters.select()).all()
    self.assertEqual(u1_follow_requesting[0].username, 'susan')
    self.assertEqual(u2_follow_requesters[0].username, 'john')

    self.u1, self.u2 = u1, u2

  @override
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_cancel_request(self):
    u1, u2 = self.u1, self.u2

    u1.cancel_follow_request(u2)
    db.session.commit()
    self.assertFalse(u1.is_follow_requesting(u2))
    self.assertFalse(u2.is_follow_requested_by(u1))
    self.assertEqual(u1.follow_requesting_count(), 0)
    self.assertEqual(u2.follow_requesters_count(), 0)
    self.assertFalse(u1.is_following(u2))
    self.assertFalse(u2.is_followed_by(u1))
    self.assertEqual(u1.following_count(), 0)
    self.assertEqual(u2.followers_count(), 0)

  def test_dismiss_request(self):
    u1, u2 = self.u1, self.u2

    u2.dismiss_follow_requester(u1)
    db.session.commit()
    self.assertFalse(u1.is_follow_requesting(u2))
    self.assertFalse(u2.is_follow_requested_by(u1))
    self.assertEqual(u1.follow_requesting_count(), 0)
    self.assertEqual(u2.follow_requesters_count(), 0)
    self.assertFalse(u1.is_following(u2))
    self.assertFalse(u2.is_followed_by(u1))
    self.assertEqual(u1.following_count(), 0)
    self.assertEqual(u2.followers_count(), 0)

  def test_follow_stop(self):
    u1, u2 = self.u1, self.u2

    u2.accept_follow_requester(u1)
    db.session.commit()
    self.assertFalse(u1.is_follow_requesting(u2))
    self.assertFalse(u2.is_follow_requested_by(u1))
    self.assertTrue(u1.is_following(u2))
    self.assertTrue(u2.is_followed_by(u1))
    self.assertEqual(u1.follow_requesting_count(), 0)
    self.assertEqual(u2.follow_requesters_count(), 0)
    self.assertEqual(u1.following_count(), 1)
    self.assertEqual(u2.followers_count(), 1)
    u1_following = db.session.scalars(u1.following.select()).all()
    u2_followers = db.session.scalars(u2.followers.select()).all()
    self.assertEqual(u1_following[0].username, 'susan')
    self.assertEqual(u2_followers[0].username, 'john')

    u1.stop_following(u2)
    db.session.commit()
    self.assertFalse(u1.is_following(u2))
    self.assertFalse(u2.is_followed_by(u1))
    self.assertEqual(u1.following_count(), 0)
    self.assertEqual(u2.followers_count(), 0)

  def test_follow_remove(self):
    u1, u2 = self.u1, self.u2

    u2.accept_follow_requester(u1)
    db.session.commit()
    self.assertFalse(u1.is_follow_requesting(u2))
    self.assertFalse(u2.is_follow_requested_by(u1))
    self.assertTrue(u1.is_following(u2))
    self.assertTrue(u2.is_followed_by(u1))
    self.assertEqual(u1.follow_requesting_count(), 0)
    self.assertEqual(u2.follow_requesters_count(), 0)
    self.assertEqual(u1.following_count(), 1)
    self.assertEqual(u2.followers_count(), 1)
    u1_following = db.session.scalars(u1.following.select()).all()
    u2_followers = db.session.scalars(u2.followers.select()).all()
    self.assertEqual(u1_following[0].username, 'susan')
    self.assertEqual(u2_followers[0].username, 'john')

    u2.remove_follower(u1)
    db.session.commit()
    self.assertFalse(u1.is_following(u2))
    self.assertFalse(u2.is_followed_by(u1))
    self.assertEqual(u1.following_count(), 0)
    self.assertEqual(u2.followers_count(), 0)


if __name__ == '__main__':
  unittest.main(verbosity=2)
