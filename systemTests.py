import threading
import unittest
import time
import os

#from app.controllers import try_to_login_user
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

    self.server_thread = threading.Thread(
        target=self.testApplication.run,
        kwargs={'debug': False, 'use_reloader': False}
    )
    self.server_thread.daemon = True
    self.server_thread.start()
    time.sleep(1)  # Give the server time to start

    self.driver = webdriver.Chrome()

    return super().setUp()
  
  def add_user(self, username, email, password):
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
  

  '''def test_login_page(self):
    self.driver.get(local_host + '/login')

    user_id_field = self.driver.find_element(By.NAME, 'username')
    password_field = self.driver.find_element(By.NAME, 'password')
    submit_button = self.driver.find_element(By.ID, 'submit')

    user_id_field.send_keys('testuser')
    password_field.send_keys('testpassword')
    submit_button.click()

    time.sleep(10)'''

  def test_upload_page(self):
    # Go to login page
    self.driver.get(local_host + '/login')
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'username'))
    ).send_keys('testuser')
    self.driver.find_element(By.NAME, 'password').send_keys('testpassword')
    self.driver.find_element(By.ID, 'submit').click()

    self.driver.find_element(By.LINK_TEXT, 'View').click()

    # Wait for the upload button to appear after login and click it
    # Adjust the selector below to match your actual upload button
    upload_btn = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'upload-btn'))  # or By.LINK_TEXT, By.CLASS_NAME, etc.
    )
    upload_btn.click()

    # Now wait for the file input on the upload page
    file_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'file')))
    zip_path = os.path.abspath("D:\FX503VM\Documents\VSCode\CITS3401_AWD\PROJECT\cits3403-group-26\tests\instagram-ben_-2025-04-30-9fGlh2CL.zip")
    file_input.send_keys(zip_path)
    submit_button = self.driver.find_element(By.ID, 'Upload')
    submit_button.click()

    time.sleep(5)


  def tearDown(self):
    self.driver.close()
    db.session.remove()
    db.drop_all()
    self.app_ctx.pop()
    return super().tearDown()

