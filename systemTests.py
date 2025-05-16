import threading
import unittest
import time
import os
import shutil

from app.models import User
from app import create_application, db
from config import TestingConfig

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

local_host = 'http://localhost:5000'

class SystemTests(unittest.TestCase):

  def setUp(self):
    self.testApplication = create_application(TestingConfig)
    self.app_ctx = self.testApplication.app_context()
    self.app_ctx.push()
    db.create_all()

    self.add_user('testuser', 'testuser@example.com', 'testpassword')
    os.makedirs('uploads', exist_ok=True)  # Ensure the folder exists
    shutil.copy('tests/testuser.json', 'uploads/testuser.json') 

    self.server_thread = threading.Thread(
        target=self.testApplication.run,
        kwargs={'debug': False, 'use_reloader': False}
    )
    self.server_thread.daemon = True
    self.server_thread.start()
    time.sleep(1)

    self.driver = webdriver.Chrome()
    return super().setUp()
  

  def add_user(self, username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


  def test_login_page(self):
    self.driver.get(local_host + '/login')

    user_id_field = self.driver.find_element(By.NAME, 'username')
    password_field = self.driver.find_element(By.NAME, 'password')
    submit_button = self.driver.find_element(By.ID, 'submit')

    user_id_field.send_keys('testuser')
    password_field.send_keys('testpassword')
    submit_button.click()

    time.sleep(5)


  def test_loggout_page(self):
    self.driver.get(local_host + '/login')
    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys('testuser')
    self.driver.find_element(By.NAME, 'password').send_keys('testpassword')
    self.driver.find_element(By.ID, 'submit').click()

    self.driver.find_element(By.LINK_TEXT, 'Logout').click()

    time.sleep(5)


  def test_register_page(self):
    self.driver.get(local_host + '/register')

    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys('newuser')
    self.driver.find_element(By.NAME, 'email').send_keys('newuser@example.com')
    self.driver.find_element(By.NAME, 'password').send_keys('newpassword')
    self.driver.find_element(By.NAME, 'password2').send_keys('newpassword')

    time.sleep(5)

    submit_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'submit')))
    self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    submit_btn.click()
  

  def test_view_data(self):
    self.driver.get(local_host + '/login')
    self.driver.find_element(By.NAME, 'username').send_keys('testuser')
    self.driver.find_element(By.NAME, 'password').send_keys('testpassword')
    self.driver.find_element(By.ID, 'submit').click()
    self.driver.find_element(By.LINK_TEXT, 'View').click()

    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'data-table')))

    time.sleep(10)
  

  def test_skip_button(self):
    self.driver.get(local_host + '/login')
    self.driver.find_element(By.NAME, 'username').send_keys('testuser')
    self.driver.find_element(By.NAME, 'password').send_keys('testpassword')
    self.driver.find_element(By.ID, 'submit').click()
    self.driver.find_element(By.LINK_TEXT, 'View').click()

    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'data-table')))

    self.driver.find_element(By.ID, 'skip-btn').click()

    time.sleep(5)
  

  def tearDown(self):
    self.driver.close()
    db.session.remove()
    db.drop_all()
    try:
        os.remove('uploads/testuser.json')
    except FileNotFoundError:
        pass
    self.app_ctx.pop()
    return super().tearDown()

