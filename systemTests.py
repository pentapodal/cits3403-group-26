import unittest

import time
from app.models import User

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

local_host =  'http://localhost:5000'

class SystemTests(unittest.TestCase):

  def setUp(self):
    testApplication = create_application(TestingConfig)
    self.app_ctx = testApplication.app_context()
    self.app_ctx.push()
    db.create_all()

    self.server_thread = multiprocessing.Process(target=self.testApplication.run)
    self.server_thread.start()

    #options = webdriver.ChromeOptions()
    #options.add_argument('--headless=new')
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
    submit_button = self.driver.find_element(By.ID 'submit')

    user_id_field.send_keys('testuser')
    password_field.send_keys('testpassword')
    submit_button.click()

    time.sleep(10)


  def tearDown(self):
    self.server_thread.terminate()
    self.driver.close()
    db.session.remove()
    db.drop_all()
    self.app_ctx.pop()
    return super().tearDown()
  
